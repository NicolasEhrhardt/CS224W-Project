from collections import Counter
from matplotlib import pyplot as plt
from graphutils import get_subgraph_by_date, get_empty_graph, add_nodes_and_edges, generate_all_graphs, generate_all_generators
import constants as cst
import numpy as np
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

    return degdist

def link_creation_by_age(graph,max_year=2014):
    """ Computes the probability of an edge linking to a node of a given age (in months) """
    links_by_age = {    
                    'user':Counter(), #key=age, value=count
                    'biz':Counter()
                    }
    nodes_age = Counter() #key=nodeId, value=age

    for nodesIter,edgesIter,criterion in generate_all_generators(graph):
        for oldNode in nodes_age:
            nodes_age[oldNode] += 1.

        for nodeId in nodesIter:
            nodes_age[nodeId] += 1.

        for edge in edgesIter:
            srcId = edge[1]
            dstId = edge[2]

            age_src = nodes_age[srcId]
            age_dst = nodes_age[dstId]

            links_by_age['user'][age_src] += 1.
            links_by_age['biz'][age_dst] += 1.

    return links_by_age
                        

def densification_exponent(graph_file='computed/graph.bin',max_year=2014):

  """ Plots the densification coefficient of the input graph. First it plot log-log plot\
    of E(t) vs N(t). The it plots the time evolution of their ration """
  
  f = snap.TFIn(graph_file)
  full_graph = snap.TNEANet.Load(f)

  nodes,edges,users,busin = nodes_and_edges_by_time(full_graph,max_year)

  # Keep nodes and edges with count > 1
  nodes = nodes[4::]
  edges = edges[4::]

  ## Compute densification exponent
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

def linreg(x, y):
    """Compute the linear regression of x and y (no bias here)"""
    return np.dot(x, y) / np.dot(x, x)

def ccdf(x):
    """Return backward cumsum"""
    y = [x[-1]]
    for i in range(1, len(x)):
        y.append(x[-1-i] + y[-1])
    y.reverse()
    return y

def alphaccdfreg(ct):
    """Compute alpha assuming that probability counter is following
    a power law p(t) \propto t^{-\alpha}, using the CCDF regression method"""

    if not ct:
        return 0
    ccdfexp = np.array(ccdf(ct.values()))
    bins = np.array(ct.keys())
    goodidx = np.where(bins > 0)

    lccdf = np.log(ccdfexp[goodidx])
    lbins = np.log(bins[goodidx])

    return 1 - linreg(lccdf, lbins)

def normalize(ct):
    """Normalize counter to probability counter"""
    tot = float(sum(ct.values()))
    for key in ct:
        ct[key] /= tot

def link_degree_density(full_graph, max_year=2014):
    """Assuming that the probability of an edge created at time t will be linked to a node of degree d
    following a law \propto d^{-alpha}, compute alpha overtime and plot for each type of node"""
    dist_time = []
    
    def counter_update(graph, nodeId, dist):
        try:
            # Some edges returned by the generator have not been added to the graph, we need to pass them
            node_type = graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_TYPE)
            deg = graph.GetNI(nodeId).GetDeg()
            dist[node_type].update([deg])
        except:
            pass
    
    for users, busin, graph, curnodes, curedges in generate_all_graphs(full_graph, detailed=True, max_year=max_year):

        dist = {cst.ATTR_NODE_USER_TYPE: Counter(), cst.ATTR_NODE_BUSINESS_TYPE: Counter()}
        for edgeId, srcId, dstId in curedges:
            counter_update(graph, srcId, dist)
            counter_update(graph, dstId, dist)

        normalize(dist[cst.ATTR_NODE_BUSINESS_TYPE])
        normalize(dist[cst.ATTR_NODE_USER_TYPE])

        dist_time.append(dist)

    useralpha = []
    businessalpha = []
    
    for dist in dist_time:
        useralpha.append(alphaccdfreg(dist[cst.ATTR_NODE_USER_TYPE]))
        businessalpha.append(alphaccdfreg(dist[cst.ATTR_NODE_BUSINESS_TYPE]))

    plt.plot(range(len(dist_time)), useralpha, label='User')
    plt.plot(range(len(dist_time)), businessalpha, label='Business')
    plt.xlabel('Month')
    plt.ylabel('Alpha')
    plt.legend()
    plt.show()


def nodes_evolution(full_graph, max_year=2014):
    """ Plots the densification coefficient of the input graph. First it plot log-log plot\
      of E(t) vs N(t). The it plots the time evolution of their ration """
    nodes,edges,users,busin = nodes_and_edges_by_time(full_graph,max_year)

    # Keep nodes and edges with count > 1
    nodes = nodes[4::]
    edges = edges[4::]

    ## Fit curve on N(t) = beta[0]*log(t) + beta[1]
    time_start = len(nodes)/3
    t = range(len(nodes))
    time = t[time_start::]
    nodes2 = nodes[time_start::]
    onez = np.ones((len(time),1))

    # solve linear regression
    lgt = np.vstack((np.log(time),onez.transpose())).transpose()
    lgy = np.log(nodes2)
    XX = np.dot(lgt.transpose(),lgt)
    Xb = np.dot(lgt.transpose(),lgy)
    beta = np.linalg.solve(XX,Xb)

    nodes_hat = np.multiply(np.power(time,beta[0]),np.exp(beta[1]))
    plt.plot(nodes,'b-',linewidth=3.)
    plt.plot(time,nodes_hat,'r--',linewidth=3.)
    plt.yscale('log')
    plt.grid(True)
    plt.xlabel('Weeks')
    plt.ylabel('Nodes')
    beta1 = int(beta[1]*100)/100.
    beta0 = int(beta[0]*100)/100.
    curve = 'exp('+str(beta1) + ')*t^' + str(beta0)
    plt.legend(('N(t)',curve))
    plt.show()


def users_vs_biz_evolution(full_graph, max_year=2014):
    """ Plots the densification coefficient of the input graph. First it plot log-log plot\
      of E(t) vs N(t). The it plots the time evolution of their ration """
    nodes,edges,users,busin = nodes_and_edges_by_time(full_graph,max_year)

    # Keep nodes and edges with count > 1
    nodes = nodes[4::]
    edges = edges[4::]

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

def nodes_and_edges_by_time(full_graph, max_year=2014,plots=False):
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

    if plots:
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

