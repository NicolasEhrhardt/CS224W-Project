from collections import Counter
from matplotlib import pyplot as plt
import snap

graph_file = 'data/graph.bin'

f = snap.TFIn(graph_file)
graph = snap.TNEANet.Load(f)

degdist = [Counter() for i in range(2)]
for n in graph.Nodes():
    node_id = n.GetId()
    node_type = graph.GetIntAttrDatN(node_id, "type")
    degdist[node_type].update([n.GetDeg()])


for d in degdist:
    plt.plot(d.keys(), d.values())

plt.legend(['User reviews', 'Business reviews'])
plt.xscale('log')
plt.xlabel('log(degree)')
plt.yscale('log')
plt.ylabel('log(count)')
plt.show()
