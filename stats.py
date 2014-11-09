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

    return degdist

def densification_exponent(graph_file='computed/graph.bin',max_year=2014):

  """ Plots the densification coefficient of the input graph. First it plot log-log plot\
    of E(t) vs N(t). The it plots the time evolution of their ration """
  
  f = snap.TFIn(graph_file)
  full_graph = snap.TNEANet.Load(f)

  nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,max_year)

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



def nodes_evolution(graph_file='computed/graph.bin',max_year=2014):

  """ Plots the densification coefficient of the input graph. First it plot log-log plot\
    of E(t) vs N(t). The it plots the time evolution of their ration """
  
  f = snap.TFIn(graph_file)
  full_graph = snap.TNEANet.Load(f)

  nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,max_year)

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


def users_vs_biz_evolution(graph_file='computed/graph.bin',max_year=2014):

  """ Plots the densification coefficient of the input graph. First it plot log-log plot\
    of E(t) vs N(t). The it plots the time evolution of their ration """
  
  f = snap.TFIn(graph_file)
  full_graph = snap.TNEANet.Load(f)

  nodes,edges,users,busin = stats.nodes_and_edges_by_time(full_graph,max_year)

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

