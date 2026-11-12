import sys; sys.path.insert(0,'.')
import fattree_k as F
import masqa_lib as L
T4 = F.build_fat_tree_k(4)
print('links', len(T4['links']), 'delay equal to lib:', bool((T4['delay']==L.TOPO['delay']).all()))
for seed in [42,43]:
    a = L.gen_traffic(100,1278.3,seed)
    b = F.gen_traffic_k(T4,100,1278.3,seed)
    same = all(x['demand']==y['demand'] and x['paths']==y['paths'] and x['pod']==y['pod'] and x['cls']==y['cls'] and x['pdelay']==y['pdelay'] for x,y in zip(a,b))
    print('seed',seed,'identical flows:',same)
