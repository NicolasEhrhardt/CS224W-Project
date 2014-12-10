from graphutils import get_empty_graph, add_nodes_and_edges, save_graph
from random import choice
import constants as cst
import numpy as np
from itertools import chain
from datetime import datetime, timedelta

def get_dt(strdate):
    """Get datetime from string"""
    if len(strdate) == 7:
        return datetime.strptime(strdate, "%Y-%m")
    else:
        return datetime.strptime(strdate, "%Y-%m-%d")


def nodesarrivalth(day):
    # time: time since beginning of yelp in months
    time = day / 30.

    beta = 1.
    mu = 2.319
    sigma = 0.4085
    #mu = 2.264
    #sigma = 1.592e-05
    alpha = 0.87

    # total number of new nodes
    new_nodes = beta* time**mu * np.exp( (sigma * np.log(time))**2/2)
    # separate ne new nodes into user nodes (nu) and business nodes (nb = nu**alpha)
    def fnodes(nu): 
        return nu + np.power(nu,alpha) - new_nodes
    
    # solve for nun using secant-method
    def nu_update(nun,h=1e-1): 
        return nun - fnodes(nun)*2*h/(fnodes(nun+h) - fnodes(nun-h))

    nun = new_nodes/2.
    while abs(nun - nu_update(nun))/nun > 1e-6:
        nun = nu_update(nun)

    new_users = nun
    new_biz = new_nodes - nun

    return (int(new_nodes), int(new_users), int(new_biz))

def get_nodesarrival_fromdata_func(name):
    number = np.loadtxt(name, delimiter=',')
    
    def get_nodes_arrival(day):
        month = int(day / 30.)
        if month >= len(number):
            month = len(number) - 1
        return int(number[month] / 30)

    return get_nodes_arrival

def get_wsample_func(name):
    population, weights = np.loadtxt(name, delimiter=',')
    return lambda: np.random.choice(population, 1, True, weights)[0]

def get_wsample_decayed_func(name, beta=0.00015):
    population, weights = np.loadtxt(name, delimiter=',')
    def get_choice(deg):
        new_weights = weights * np.exp(-beta * deg * population)
        new_weights /= new_weights.sum()
        return np.random.choice(population, 1, True, new_weights)[0]

    return get_choice


reviewdelta = get_wsample_decayed_func('computed/user_age_between_2.csv')
lifetime = get_wsample_func('computed/user_lifetime.csv')
bizarrival = get_nodesarrival_fromdata_func('computed/biz_arrival_Real.csv')
userarrival = get_nodesarrival_fromdata_func('computed/user_arrival_Real.csv')

nodesarrival = lambda x: (userarrival(x), bizarrival(x))

def get_half(graph, cut=lambda x: x < '2011-01-01'):
    half_graph = get_empty_graph()
    add_nodes_and_edges(graph, half_graph, cut)
    return half_graph

def simulate(graph, 
        date_start=get_dt('2011-01-01'), date_end=get_dt('2014-07-01'), month_start=75,
        lifetime=lifetime, reviewdelta=reviewdelta, nodesarrival=nodesarrival,
        nodelifetime=None, nodewakeup=None):

    init_times = nodelifetime is None or nodewakeup is None

    if init_times:
        nodelifetime = dict()
        nodewakeup = dict()

    nb_users = 0
    nb_bizs = 0
    day = month_start * 30

    print ">> Computing node counts and init time gaps"
    for node in graph.Nodes():
        if graph.GetStrAttrDatN(node.GetId(), cst.ATTR_NODE_TYPE) == cst.ATTR_NODE_USER_TYPE:
            createddatestr = graph.GetStrAttrDatN(node.GetId(), cst.ATTR_NODE_CREATED_DATE)

            if init_times:
                nodelifetime[node.GetId()] =  (get_dt(createddatestr) - get_dt('2004-01-01')).days + lifetime()
                nodewakeup[node.GetId()] = (createddatestr, node.GetDeg()) # day + reviewdelta(node.GetDeg())

            nb_users += 1
        else:
            nb_bizs += 1

    print ">> Init lifetimes"
    for edge in graph.Edges():
        testdatestr = graph.GetStrAttrDatE(edge.GetId(), cst.ATTR_EDGE_REVIEW_DATE)
        userId = edge.GetSrcNId()

        if nodewakeup[userId][0] < testdatestr:
            nodewakeup[userId] = (testdatestr, nodewakeup[userId][1])

    for userId in nodewakeup:
        mostrecentrev, deg = nodewakeup[userId]
        lastrevday = (get_dt(mostrecentrev) - get_dt('2004-01-01')).days

        nodelifetime[userId] = lastrevday + reviewdelta(deg)

    def add_node(node_type, date, d):
        # adding node and metadata
        new_nodeId = graph.AddNode()
        graph.AddStrAttrDatN(new_nodeId, node_type, cst.ATTR_NODE_TYPE)
        graph.AddStrAttrDatN(new_nodeId, date, cst.ATTR_NODE_CREATED_DATE)

        if node_type == cst.ATTR_NODE_USER_TYPE:
            # set lifetime and wake-up time
            nodelifetime[new_nodeId] = d + lifetime()
            nodewakeup[new_nodeId] = d + reviewdelta(0)

        return new_nodeId

    def add_edge(srcId, dstId, date):
        edgeId = graph.AddEdge(srcId, dstId)
        graph.AddStrAttrDatE(edgeId, date, cst.ATTR_EDGE_REVIEW_DATE)
        return edgeId

    print ">> Starting alg"

    all_delta_reviews = []
    all_delta_users = []
    all_delta_bizs = []

    delta = timedelta(days=1)
    while date_start <= date_end:
        date_start += delta
        day += 1.
        datestr = date_start.strftime("%Y-%m-%d")
        # Step 1. Add new nodes
        
        delta_users, delta_bizs = nodesarrival(day)

        # Step 2. 3. 4. Sample life time, link new nodes using PA, Sample wakeup time 
        
        for _ in range(delta_users):
            new_nodeId = add_node(cst.ATTR_NODE_USER_TYPE, datestr, day)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_BUSINESS_TYPE)
            add_edge(new_nodeId, linked_nodeId, datestr) # TODO: step to change 

        for _ in range(delta_bizs):
            new_nodeId = add_node(cst.ATTR_NODE_BUSINESS_TYPE, datestr, day)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_USER_TYPE)
            add_edge(linked_nodeId, new_nodeId, datestr) # TODO: step to change 

        delta_reviews = 0
        # Step 5. For wake up nodes, create link using random-random-random walk
        for nodeId, wakeuptime in nodewakeup.iteritems():
            if wakeuptime == day:
                # pass if node has died
                if nodelifetime[nodeId] <= day:
                    continue

                # otherwise create review
                linked_nodeId = get_random(graph, nodeId, 3) # 3 random!
                add_edge(nodeId, linked_nodeId, datestr)

                timegap = reviewdelta(graph.GetNI(nodeId).GetDeg())
                
                while timegap == 0: # keep creating review if it is the same day
                    linked_nodeId = get_random(graph, nodeId, 3) # 3 random!
                    add_edge(nodeId, linked_nodeId, datestr)
                    delta_reviews += 1
                    #while timegap == 0:
                    timegap = reviewdelta(graph.GetNI(nodeId).GetDeg())


                nodewakeup[nodeId] = day + timegap # setup new wakeup time
                delta_reviews += 1

        all_delta_users.append(delta_users)
        all_delta_bizs.append(delta_bizs)
        all_delta_reviews.append(delta_reviews)

        print ">> Day %s, Added users %d, Added biz %d, Added reviews %d" % \
            (day, delta_users, delta_bizs, delta_reviews)

        nb_users += delta_users
        nb_bizs += delta_bizs
    
    return graph, nodelifetime, nodewakeup, nb_users, nb_bizs, month_start

def get_PA(graph, node_type):
    nodeId = graph.GetRndNId()
    while graph.GetStrAttrDatN(nodeId, cst.ATTR_NODE_TYPE) != node_type:
        nodeId = graph.GetRndNId()

    node = graph.GetNI(nodeId)
    if node.GetDeg() == 0:
        return node.GetId()
    else:
        neighborIds = [neighborId for neighborId in chain(node.GetOutEdges(), node.GetInEdges())]
        return choice(neighborIds)

def get_random(graph, nodeId, jump):
    node = graph.GetNI(nodeId)
    if node.GetDeg() == 0:
        return get_PA(graph, cst.ATTR_NODE_BUSINESS_TYPE)

    if jump == 0:
        return nodeId
    
    neighborIds = [neighborId for neighborId in chain(node.GetOutEdges(), node.GetInEdges())]

    return get_random(graph, choice(neighborIds), jump - 1)
