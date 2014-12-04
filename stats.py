from collections import Counter
from matplotlib import pyplot as plt
from graphutils import get_empty_graph, add_nodes_and_edges, generate_all_graphs, generate_all_generators
import constants as cst
import numpy as np
import snap
from datetime import datetime

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

def lifetime(full_graph):
    alldates = {
        cst.ATTR_NODE_USER_TYPE: Counter(),
        cst.ATTR_NODE_BUSINESS_TYPE: Counter(),
    }

    def get_dt(strdate):
        """Get datetime from string"""
        if len(strdate) == 7:
            return datetime.strptime(strdate, "%Y-%m")
        else:
            return datetime.strptime(strdate, "%Y-%m-%d")

    def get_lifetime(x):
        """From a list of score x, get the lifetime of node
        >>> get_lifetime([2,1,3], 1)
        2
        """
        y = sorted(x)
        return (y[-1] - y[1]).days
    
    jumpednodes = 0

    for node in full_graph.Nodes():
        nodeId = node.GetId()
        if node.GetDeg() == 0:
            continue

        created_strdate = full_graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_CREATED_DATE)
        node_type = full_graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_TYPE)

        #if node_type == cst.ATTR_NODE_USER_TYPE and full_graph.GetIntAttrDatN(nodeId, cst.ATTR_NODE_ELITE_YEAR) == cst.ATTR_NOT_ELITE:
        #    jumpednodes += 1
        #    continue

        created_dt = get_dt(created_strdate)
        nodereviews = [created_dt]

        # For users
        for neighborId in node.GetOutEdges():
            edgeId = full_graph.GetEId(nodeId, neighborId)
            review_strdate = full_graph.GetStrAttrDatE(edgeId, cst.ATTR_EDGE_REVIEW_DATE)
            review_dt = get_dt(review_strdate)
            delta = (review_dt - created_dt).days
            if delta < 0:
                continue

            nodereviews.append(review_dt)

        # For businesses
        for neighborId in node.GetInEdges():
            edgeId = full_graph.GetEId(neighborId, nodeId)
            review_strdate = full_graph.GetStrAttrDatE(edgeId, cst.ATTR_EDGE_REVIEW_DATE)
            review_dt = get_dt(review_strdate)
            delta = (review_dt - created_dt).days
            if delta < 0:
                continue

            nodereviews.append(review_dt)

        if nodereviews and len(nodereviews) > 1:
            alldates[node_type].update([get_lifetime(nodereviews)])

    print jumpednodes

    for node_type, dist in alldates.iteritems():
        normalize(dist)
        X, Y = dist_from_counter(dist)
        plt.plot(X, Y, label=node_type)

    plt.legend()
    plt.xlabel('Lifetime')
    plt.xscale('log')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.show()

def age_between_review(full_graph, nreview=0):
    alldates = {
        cst.ATTR_NODE_USER_TYPE: Counter(),
        cst.ATTR_NODE_BUSINESS_TYPE: Counter(),
    }

    def get_dt(strdate):
        """Get datetime from string"""
        if len(strdate) == 7:
            return datetime.strptime(strdate, "%Y-%m")
        else:
            return datetime.strptime(strdate, "%Y-%m-%d")

    def get_time_between(x, rank=1):
        """From a list of score x, get the value of a certain rank:
        >>> get_time_between([2,1,3], 1)
        2
        """
        y = sorted(x)
        if rank == 0:
            return [ (y[rank] - y[rank-1]).days for rank in range(1,len(y)) ]
        else:
            return [(y[rank] - y[rank-1]).days]
    
    jumpednodes = 0
    def save_to_csv(X,Y):
        np

    def get_delta(egdeId, created_dt):
        """return time delta"""
        review_strdate = full_graph.GetStrAttrDatE(edgeId, cst.ATTR_EDGE_REVIEW_DATE)
        review_dt = get_dt(review_strdate)
        return (review_dt - created_dt).days

    for node in full_graph.Nodes():
        nodeId = node.GetId()
        if node.GetDeg() == 0:
            continue

        created_strdate = full_graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_CREATED_DATE)
        node_type = full_graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_TYPE)

        #if node_type == cst.ATTR_NODE_USER_TYPE and full_graph.GetIntAttrDatN(nodeId, cst.ATTR_NODE_ELITE_YEAR) == cst.ATTR_NOT_ELITE:
        #    jumpednodes += 1
        #    continue

        created_dt = get_dt(created_strdate)
        nodereviews = [created_dt]

        # For users
        for neighborId in node.GetOutEdges():
            edgeId = full_graph.GetEId(nodeId, neighborId)
            review_strdate = full_graph.GetStrAttrDatE(edgeId, cst.ATTR_EDGE_REVIEW_DATE)
            review_dt = get_dt(review_strdate)
            delta = (review_dt - created_dt).days
            if delta < 0:
                continue

            nodereviews.append(review_dt)

        # For businesses
        for neighborId in node.GetInEdges():
            edgeId = full_graph.GetEId(neighborId, nodeId)
            review_strdate = full_graph.GetStrAttrDatE(edgeId, cst.ATTR_EDGE_REVIEW_DATE)
            review_dt = get_dt(review_strdate)
            delta = (review_dt - created_dt).days
            if delta < 0:
                continue

            nodereviews.append(review_dt)

        if nodereviews and len(nodereviews) > nreview:            
            alldates[node_type].update(get_time_between(nodereviews, rank=nreview))

    print jumpednodes

    for node_type, dist in alldates.iteritems():
        normalize(dist)
        X, Y = dist_from_counter(dist)
        array_age_dist = np.asarray([X,Y])
        name = node_type+"_age_between_"+str(nreview)
        np.savetxt('computed/'+name+".csv",array_age_dist,delimiter=",")
        plt.ylim([0,max(Y)+0.01])
        plt.yscale('log')
        plt.plot(X, Y, label=node_type)


    plt.legend()
    plt.xlabel('Number of days between reviews (%d, %d)' % (nreview, nreview+1))
    plt.xscale('log')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.savefig('analysis/'+name+'.png')
    plt.show()

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
            if nodeId not in nodes_age:
                nodes_age[nodeId] = 1.

        for edgeId, srcId, dstId in edgesIter:
            age_src = nodes_age[srcId]
            age_dst = nodes_age[dstId]

            links_by_age['user'][age_src] += 1.
            links_by_age['biz'][age_dst] += 1.

    plt.plot(links_by_age['user'].keys(), links_by_age['user'].values(), label='User')
    plt.plot(links_by_age['biz'].keys(), links_by_age['biz'].values(), label='Business')
    plt.yscale('log')
    plt.xlabel('age')
    plt.ylabel('log(count)')
    plt.legend()
    plt.show()

    return links_by_age

def densification_exponent(full_graph, max_year=2014):
    """ Plots the densification coefficient of the input graph. First it plot log-log plot\
            of E(t) vs N(t). The it plots the time evolution of their ration """
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

def dist_from_counter(ct):
    return zip(*sorted(ct.items()))

def link_degree(full_graph, max_year=2014):
    """Assuming that the probability of an edge created at time t will be linked to a node of degree d
    following a law \propto d^{-alpha}, compute alpha overtime and plot for each type of node"""
    
    def counter_update(graph, nodeId, dist):
        try:
            # Some edges returned by the generator have not been added to the graph, we need to pass them
            node_type = graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_TYPE)
            deg = graph.GetNI(nodeId).GetDeg()
            dist[node_type].update([deg])
        except:
            pass

    dist = {cst.ATTR_NODE_USER_TYPE: Counter(), cst.ATTR_NODE_BUSINESS_TYPE: Counter()}
    for users, busin, graph, curnodes, curedges in generate_all_graphs(full_graph, detailed=True, max_year=max_year):
        for edgeId, srcId, dstId in curedges:
            counter_update(graph, srcId, dist)
            counter_update(graph, dstId, dist)

    normalize(dist[cst.ATTR_NODE_BUSINESS_TYPE])
    normalize(dist[cst.ATTR_NODE_USER_TYPE])

    Xb, Yb = dist_from_counter(dist[cst.ATTR_NODE_BUSINESS_TYPE])
    Xu, Yu = dist_from_counter(dist[cst.ATTR_NODE_USER_TYPE])
    plt.plot(Xu, Yu, label='User')
    plt.plot(Xb, Yb, label='Business')
    #plt.xscale('log')
    plt.xlabel('Node degre')
    #plt.yscale('log')
    plt.ylabel('Ratio of links created this month')
    plt.legend()
    plt.show()

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

    i = 1
    for dist in dist_time:
        if i % 12 == 0 and dist[cst.ATTR_NODE_USER_TYPE] and dist[cst.ATTR_NODE_BUSINESS_TYPE]:
            Xu, Yu = zip(*sorted(dist[cst.ATTR_NODE_USER_TYPE].items()))
            Xb, Yb = zip(*sorted(dist[cst.ATTR_NODE_BUSINESS_TYPE].items()))
            plt.plot(Xu, Yu, label='User')
            plt.plot(Xb, Yb, label='Business')
            plt.xscale('log')
            plt.xlabel('Node degre')
            plt.yscale('log')
            plt.ylabel('Ratio of links created this month')
            plt.legend()
            plt.show()

        i += 1
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

    ## Fit curve on N(t) = beta[0]*log(t) + beta[1]
    time_start = len(nodes)/5
    time = range(time_start, len(nodes))

    def get_approx(time, nodes):
        onez = np.ones((len(time),1))

        # solve linear regression
        lgt = np.vstack((np.log(time),onez.transpose())).transpose()
        lgy = np.log(nodes)
        XX = np.dot(lgt.transpose(),lgt)
        Xb = np.dot(lgt.transpose(),lgy)
        beta = np.linalg.solve(XX,Xb)

        nodes_hat = np.multiply(np.power(time,beta[0]),np.exp(beta[1]))
        return nodes_hat, beta

    users_hat, betau = get_approx(time, users[time_start::])
    busin_hat, betab = get_approx(time, busin[time_start::])

    plt.plot(users, 'b-', linewidth=3., label="Users")
    plt.plot(busin, 'g-', linewidth=3., label="Businesses")

    labelau = "exp(%f)*t^%f" % tuple(map(lambda x: round(x, 2), reversed(betau)))
    plt.plot(time, users_hat, 'r--', linewidth=3., label=labelau)
    labelab = "exp(%f)*t^%f" % tuple(map(lambda x: round(x, 2), reversed(betab)))
    plt.plot(time, busin_hat, 'r--', linewidth=3., label=labelab)
    
    plt.yscale('log')
    plt.xlabel('Months')
    plt.ylabel('Count of Nodes')
    #curve = 'exp('+str(beta1) + ')*t^' + str(beta0)
    plt.legend(loc=4)
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

def diam_by_time(full_graph, min_year=2005, max_year=2014):
    diamsz = []

    for users, busin, graph in generate_all_graphs(full_graph, min_year=min_year, max_year=max_year):
        diamsz.append(snap.GetBfsFullDiam(graph, 40))

    plt.plot(diamsz)
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
