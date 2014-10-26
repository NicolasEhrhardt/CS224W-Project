from collections import Counter
from matplotlib import pyplot as plt
import snap

graph_file = 'computed/graph.bin'

f = snap.TFIn(graph_file)
graph = snap.TNEANet.Load(f)

degdist = {
    'user': Counter(),
    'business': Counter()
}

for n in graph.Nodes():
    node_id = n.GetId()
    node_type = graph.GetStrAttrDatN(node_id, "type")
    degdist[node_type].update([n.GetDeg()])

print("> Displaying dist")
for node_type, d in degdist.iteritems():
    plt.plot(d.keys(), d.values())

plt.legend(['User reviews', 'Business reviews'])
plt.xscale('log')
plt.xlabel('log(degree)')
plt.yscale('log')
plt.ylabel('log(count)')
plt.show()
