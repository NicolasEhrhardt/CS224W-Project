import workspace
import stats
import graphutils
import snap
from graphutils import delete_node_type, get_subgraph_by_date, copy_graph
from projection import projection
import numpy as np
import matplotlib.pyplot as plt

graph_file = 'computed/graph.bin'

f = snap.TFIn(graph_file)
full_graph = snap.TNEANet.Load(f)

nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,2014)

# Keep nodes and edges with count > 1
nodes = nodes[4::]
edges = edges[4::]

## Compute densification exponent
idx_start = 0

plt.plot(nodes,edges,'ob-',linewidth=3.)
plt.yscale('log')
plt.xscale('log')
plt.xlabel('log N(t)')
plt.ylabel('log E(t)')
plt.grid(True)
plt.show()

# plot empirical densification exponent
dens_exp = [np.log(edges[idx])/np.log(nodes[idx]) for idx in range(len(nodes))]
plt.plot(dens_exp,'s--',linewidth=3.)
plt.xlabel('t')
plt.ylabel('log N(t) / log E(t)')
plt.grid(True)
plt.show()


## Fit curve on N(t)
tpart2 = len(nodes)/3
t = range(len(nodes))
t2 = t[tpart2::]
nodes2 = nodes[tpart2::]
onez = np.ones((len(t2),1))

lgt = np.vstack((np.log(t2),onez.transpose())).transpose()
lgy = np.log(nodes2)
XX = np.dot(lgt.transpose(),lgt)
Xb = np.dot(lgt.transpose(),lgy)
beta = np.linalg.solve(XX,Xb)

nodes_hat = np.multiply(np.power(t2,beta[0]),np.exp(beta[1]))
plt.plot(nodes,'b-',linewidth=3.)
plt.plot(t2,nodes_hat,'r--',linewidth=3.)
plt.yscale('log')
plt.grid(True)
plt.xlabel('Weeks')
plt.ylabel('Nodes')
beta1 = int(beta[1]*100)/100.
beta0 = int(beta[0]*100)/100.
curve = 'exp('+str(beta1) + ')*t^' + str(beta0)
plt.legend(('N(t)',curve))
plt.show()

## users vs businesses
users = users[4::]
busin = busin[4::]
ratio_user_biz = [np.log(users[idx])/np.log(busin[idx]) for idx in range(len(users))]
plt.plot(ratio_user_biz,linewidth=3.)
plt.plot([0,len(ratio_user_biz)], [ratio_user_biz[-1], ratio_user_biz[-1]],'r--',linewidth=3.)
plt.xlabel('weeks')
plt.ylabel('log(nusers)/log(nbiz)')
plt.legend(('Observed','1.167'))
plt.show()



