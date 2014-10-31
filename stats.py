from collections import Counter
from matplotlib import pyplot as plt
from graphutils import get_subgraph_by_date
import snap

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

def diam_by_time(graph, years=[]):
    diamsz = {}

    for year in years:
        print('> Computing year %d' % year)
        ng = get_subgraph_by_date(graph, lambda x: x < str(year+1) + '-01-01')
        diamsz[year] = snap.GetBfsFullDiam(ng, 20)

    yearstr = [str(y) for y in years]
    plt.plot(yearstr, diamsz.values())
    plt.xlabel('Year')
    plt.ylabel('Diameter')
    plt.show()

def raw_stats(graph):
    reviewcounts = Counter()
    usercounts = Counter()
    businesscounts = Counter()

    for edge in graph.Edges():
        year = graph.GetStrAttrDatE(edge.GetId(), 'date')[0:4]
        reviewcounts.update([year])

    t = True
    for node in graph.Nodes():
        year = graph.GetStrAttrDatN(node.GetId(), 'date')[0:4]
        tipe = graph.GetStrAttrDatN(node.GetId(), 'type')
        if tipe == 'user':
            usercounts.update([year])
        else:
            if year == '' and t:
                print node.GetId()
                t ^= True

            businesscounts.update([year])

    usery, userc = zip(*sorted(usercounts.items()))
    businessy, businessc = zip(*sorted(businesscounts.items()))
    reviewy, reviewc = zip(*sorted(reviewcounts.items()))

    plt.plot(usery, userc, label='User counts')
    plt.plot(businessy, businessc, label='Business counts')
    plt.plot(reviewy, reviewc, label='Review counts')
    plt.legend()
    plt.show()

