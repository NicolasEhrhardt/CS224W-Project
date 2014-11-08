import workspace
import stats
import graphutils
import snap
from graphutils import delete_node_type, get_subgraph_by_date, copy_graph
from projection import projection
import numpy as np
import matplotlib.pyplot as plt

"""
graph_file = 'computed/graph.bin'

f = snap.TFIn(graph_file)
full_graph = snap.TNEANet.Load(f)

dates = []

for year in range(2004,2014):
    for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        date = str(year) + '-' + month + '-' + '01'
        dates.append(date)

dates = dates[10::]
nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,dates)

nodes = nodes[1::]
edges = edges[1::]
"""

## Compute densification exponent
lgedges = np.log(edges)
lgnodes = np.log(nodes)
onez = np.ones((len(edges),1))
Xde = np.vstack(lgedges,onez.transpose()).transpose()
XXde = np.dot(Xde.transpose(),Xde)
Xbde = np.dot(Xde.transpose(),lgnodes)
betade = np.linalg.solve(XXde,Xbde)

lgedges_hat = np.dot(Xde,betade.transpose())
edges_hat = np.exp(lgedges_hat)
plt.plot(nodes,edges,'b-',linewidth=3)
plt.plot(nodes,edges_hat,'r--',linewidth=3)
plt.yscale('log')
plt.xscale('log')
plt.grid(True)
plt.show()

## Fit curve on N(t)
tpart2 = len(nodes)/2
t = range(len(nodes))
t2 = t[tpart2::]
nodes2 = nodes[tpart2::]
onez = np.ones((len(t2),1))

lgt = np.vstack((np.log(t2),onez)).transpose()
lgy = np.log(nodes2)
XX = np.dot(lgt.transpose(),lgt)
Xb = np.dot(lgt.transpose(),nodes2)
beta = np.linalg.solve(XX,Xb)

nodes_hat = np.multiply(np.power(t2,beta[0]),np.exp(beta[1]))
plt.plot(nodes,'b-',linewidth=3.)
plt.plot(t2,nodes_hat,'r--',linewidth=3.)
plt.grid(True)
plt.show()
plt.xlabel('Weeks')
plt.ylabel('Nodes')


