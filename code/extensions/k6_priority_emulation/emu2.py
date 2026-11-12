import os
# Kernel-forwarding emulation of the k=4 Fat-Tree. Every switch is a Mininet node with ip_forward=1.
# Each flow gets its own source alias (on the source host) and destination alias (on the destination host),
# so per-flow paths are static /32 routes on the switches. No OpenFlow, no OVS.
import sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
import numpy as np, time
import fattree_k as F

def _ipof(k, side):  # /30 per physical link: side 1 -> .1, side 2 -> .2
    return k

class Emu:
    def __init__(self, T, scale):
        self.T = T; self.scale = scale
        self.names = sorted({tuple(sorted(k)) for k in T['links']})
        self.link_no = {pair: i for i, pair in enumerate(self.names)}
        self.net = Mininet(link=TCLink, controller=None, autoSetMacs=True)
        self.node = {}
        for pair in self.names:
            for n in pair:
                if n not in self.node:
                    self.node[n] = self.net.addHost(n)
        self.intf = {}   # (u, v) -> interface name on u toward v
        self.ipof = {}   # (u, v) -> IP of v's side of the u-v link
        self.ownip = {}  # (u, v) -> IP of u's side
        for (u, v) in self.names:
            i = self.link_no[(u, v)]
            ip_u, ip_v = f"192.168.{i//64}.{(i%64)*4+1}", f"192.168.{i//64}.{(i%64)*4+2}"
            self.net.addLink(self.node[u], self.node[v], cls=TCLink, bw=50.0*scale,
                             params1={'ip': f"{ip_u}/30"}, params2={'ip': f"{ip_v}/30"})
            self.intf[(u, v)] = self.node[u].connectionsTo(self.node[v])[0][0].name
            self.intf[(v, u)] = self.node[v].connectionsTo(self.node[u])[0][0].name
            self.ipof[(u, v)] = ip_v; self.ipof[(v, u)] = ip_u
            self.ownip[(u, v)] = ip_u; self.ownip[(v, u)] = ip_v
        self.net.start()
        for (u, v), dev in self.intf.items():
            self.node[u].cmd(f"ip addr flush dev {dev}; ip addr add {self.ownip[(u, v)]}/30 dev {dev}")
        for n in self.node.values():
            n.cmd('sysctl -qw net.ipv4.ip_forward=1; sysctl -qw net.ipv4.conf.all.rp_filter=0; sysctl -qw net.ipv4.conf.default.rp_filter=0')
            n.cmd('for i in $(ls /sys/class/net | grep -v lo); do sysctl -qw net.ipv4.conf.$i.rp_filter=0; ethtool -K $i tx off rx off tso off gso off gro off >/dev/null 2>&1; done')
        # default route on each host toward its edge switch
        for h in [n for n in self.node if n.startswith('h')]:
            edge = [x for x in self.node if x.startswith('e') and (h, x) in self.intf][0]
            self.node[h].cmd(f"ip route add default via {self.ipof[(h, edge)]}")

    def hostdev(self, h):
        edge = [x for x in self.node if (h, x) in self.intf][0]
        return self.intf[(h, edge)]

    def install(self, flows, assign, sel):
        """Aliases and /32 routes for the selected flows (chosen path). Returns alias addresses per flow."""
        addr = {}
        for f in flows:
            if f['id'] not in sel: continue
            i = f['id']
            sa, da = f"10.10.{i//250}.{i%250+1}", f"10.20.{i//250}.{i%250+1}"
            addr[i] = (sa, da)
            arcs = f['paths'][assign[i]]
            inv = {v: k for k, v in self.T['links'].items()}
            seq = [inv[arcs[0]][0]] + [inv[a][1] for a in arcs]     # node sequence h, e, a, c, a', e', h'
            self.node[f['src']].cmd(f"ip addr add {sa}/32 dev {self.hostdev(f['src'])}")
            self.node[f['dst']].cmd(f"ip addr add {da}/32 dev {self.hostdev(f['dst'])}")
            for k in range(1, len(seq) - 1):
                s, nxt, prv = seq[k], seq[k+1], seq[k-1]
                self.node[s].cmd(f"ip route add {da}/32 via {self.ipof[(s, nxt)]} dev {self.intf[(s, nxt)]}")
                self.node[s].cmd(f"ip route add {sa}/32 via {self.ipof[(s, prv)]} dev {self.intf[(s, prv)]}")
        return addr

    def clear(self):
        for n in self.node.values():
            if n.name.startswith(('e', 'a', 'c')):
                n.cmd('ip route flush table main proto static 2>/dev/null; ip route flush 10.20.0.0/16 2>/dev/null; ip route flush 10.10.0.0/16 2>/dev/null')


    def run(self, flows, addr, scale, dur):
        srv = []; cli = {}
        for f in flows:
            if f['id'] not in addr: continue
            sa, da = addr[f['id']]; p = 5000 + f['id']
            srv.append(self.node[f['dst']].popen(['iperf3', '-s', '-B', da, '-p', str(p), '-1'],
                                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(2.0)
        for f in flows:
            if f['id'] not in addr: continue
            sa, da = addr[f['id']]; p = 5000 + f['id']
            cli[f['id']] = self.node[f['src']].popen(
                ['iperf3', '-c', da, '-B', sa, '-p', str(p), '-u', '-b', f"{f['demand']*scale:.4f}M", '-t', str(dur), '-J'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        res = {}
        for fid, pr in cli.items():
            out, _ = pr.communicate(timeout=dur + 90)
            try:
                s = json.loads(out)['end']['sum']
                res[fid] = dict(bps=s['bits_per_second'], lost_pct=s.get('lost_percent', float('nan')))
            except Exception:
                res[fid] = dict(bps=float('nan'), lost_pct=float('nan'))
        for s in srv: s.wait()
        return res

    def stop(self):
        self.net.stop(); subprocess.run(['mn', '-c'], capture_output=True)
