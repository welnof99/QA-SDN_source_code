import os
import sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, fattree_k as F, masqa_lib as L
import emu2
from mininet.log import setLogLevel; setLogLevel('error')
scale=float(sys.argv[1]); seed=int(sys.argv[2]); dur=int(sys.argv[3]); nmax=int(sys.argv[4])
T=F.build_fat_tree_k(4); L.TOPO=T; N,D=L.SCENARIOS['S2']
flows=F.gen_traffic_k(T,N,D,seed); adm=L.ecmp_admission(flows,seed)
sel=set(sorted(i for i,p in adm.items() if p is not None)[:nmax])
e=emu2.Emu(T,scale)
addr=e.install(flows,adm,sel)
res=e.run(flows,addr,scale,dur)
lost=[r['lost_pct'] for r in res.values() if r['lost_pct']==r['lost_pct']]
nan=sum(1 for r in res.values() if r['lost_pct']!=r['lost_pct'])
print(f'RESULT scale={scale} sent={len(sel)} nan={nan} n_loss>1%={sum(l>1 for l in lost)} mean_loss={np.mean(lost):.2f}', flush=True)
e.stop()
