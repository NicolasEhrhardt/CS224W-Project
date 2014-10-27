from collections import Counter
from matplotlib import pyplot as plt

def degree_dist(graph):
    degdist = {
        'user': Counter(),
        'business': Counter()
    }

    for n in graph.Nodes():
        node_id = n.GetId()
        node_type = graph.GetStrAttrDatN(node_id, "type")
        degdist[node_type].update([n.GetDeg()])

    for node_type, d in degdist.iteritems():
        plt.plot(d.keys(), d.values())

    plt.legend(['User reviews', 'Business reviews'])
    plt.xscale('log')
    plt.xlabel('log(degree)')
    plt.yscale('log')
    plt.ylabel('log(count)')
    plt.show()
