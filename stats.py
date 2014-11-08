from collections import Counter
from matplotlib import pyplot as plt
from graphutils import get_subgraph_by_date, get_empty_graph, add_nodes_and_edges, generate_all_graphs
from utils import disp
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

def clustr_coeff_by_time(full_graph,dates=[]):
    "Dates is a sorted iterable of dates at the format YYYY-MM-DD. The function will incrementally \
     build a graph by adding edges and nodes according the dates in dates. For each date, the function \
     will store the clustering coefficient of the graph"

    graph = get_empty_graph()
    n_dates = len(dates)
    clustr_coeffs = [0]*n_dates
    for idate in range(n_dates):
        print('> Computing year %s' % dates[idate])
        add_nodes_and_edges(full_graph,graph, lambda x : x < dates[idate] )
        clustr_coeffs[idate] = snap.GetClustCf(graph)

    plt.plot(clustr_coeffs)
    plt.xticks(range(len(clustr_coeffs)),dates,size='small')
    plt.show()

def nodes_and_edges_by_time(full_graph, max_year=2014):
    "Dates is a sorted iterable of dates at the format YYYY-MM-DD. The function will incrementally \
     build a graph by adding edges and nodes according the dates in dates. For each date, the function \
     will store the number of nodes/edges created"

    nodes = [0]
    edges = [0]
    nusers = [0]
    nbusin = [0]
    for users, busin, graph in generate_all_graphs(full_graph, max_year=max_year):
        nodes.append(graph.GetNodes())
        edges.append(graph.GetEdges())
        
        nusers.append(nusers[-1] + users)
        nbusin.append(nbusin[-1] + busin)
    
    nodes_rate = [ nodes[i+1] - nodes[i] for i in range(len(nodes)-1) ]
    edges_rate = [ edges[i+1] - edges[i] for i in range(len(edges)-1) ]

    plt.plot(nodes_rate,'b-')
    plt.plot(edges_rate,'m--')
    plt.legend(('nodes creation rate','edge creation rate'))
    plt.show()

    plt.plot(nodes,'b-')
    plt.plot(edges,'m--')
    plt.legend(('nodes','edges'))
    plt.xlabel('month')
    plt.ylabel('count')
    plt.show()

    plt.plot(nusers,'b-')
    plt.plot(nbusin,'m--')
    plt.legend(('users','businesses'))
    plt.xlabel('month')
    plt.ylabel('count')
    plt.show()

    return (nodes,edges,nusers,nbusin)

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

