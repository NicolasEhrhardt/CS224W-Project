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


def nodesarrival(day):
    # time: time since beginning of yelp in months
    time = day / 30.

    beta = 1.
    mu = 2.319
    sigma = 0.4085
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

dist_between = np.loadtxt('computed/user_age_between_0.csv',delimiter=',')
weights_between = dist_between[1]
population_between = dist_between[0]
reviewdelta = lambda: np.random.choice(population_between, 1, True, weights_between)[0]

dist_lifetime = np.loadtxt('computed/user_lifetime.csv', delimiter=',')
weights_lifetime = dist_lifetime[1]
population_lifetime = dist_lifetime[0]
lifetime = lambda: np.random.choice(population_lifetime, 1, True, weights_lifetime)[0]

def get_half(graph, cut=lambda x: x < '2011-01-01'):
    half_graph = get_empty_graph()
    add_nodes_and_edges(graph, half_graph, cut)
    return half_graph

def simulate(graph, date_start=get_dt('2011-01-01'), date_end=get_dt('2014-07-01'), month_start=77,
    lifetime=lifetime, reviewdelta=reviewdelta, nodesarrival=nodesarrival):

    nodelifetime = dict()
    nodewakeup = dict()
    nb_users = 0
    nb_bizs = 0

    print "Computing node counts"
    for node in graph.Nodes():
        if graph.GetStrAttrDatN(node.GetId(), cst.ATTR_NODE_TYPE) == cst.ATTR_NODE_USER_TYPE:
            nodelifetime[node.GetId()] = lifetime()
            nodewakeup[node.GetId()] = reviewdelta()
            nb_users += 1
        else:
            nb_bizs += 1

    def add_node(node_type, date):
        # adding node and metadata
        new_nodeId = graph.AddNode()
        graph.AddStrAttrDatN(new_nodeId, node_type, cst.ATTR_NODE_TYPE)
        graph.AddStrAttrDatN(new_nodeId, date, cst.ATTR_NODE_CREATED_DATE)

        if node_type == cst.ATTR_NODE_USER_TYPE:
            # set lifetime and wake-up time
            nodelifetime[new_nodeId] = lifetime()
            nodewakeup[new_nodeId] = reviewdelta()

        return new_nodeId

    def add_edge(srcId, dstId, date):
        edgeId = graph.AddEdge(srcId, dstId)
        graph.AddStrAttrDatE(edgeId, date, cst.ATTR_EDGE_REVIEW_DATE)
        return edgeId

    print "Starting alg"

    delta = timedelta(days=1)
    day = month_start * 30
    while date_start <= date_end:
        date_start += delta
        day += 1.
        # Step 1. Add new nodes
        
        aew_nb_nodes, new_nb_users, new_nb_bizs = nodesarrival(day)
        delta_users = new_nb_users - nb_users
        delta_bizs = new_nb_bizs - nb_bizs
        print "Day %s, Added users %d, Added biz %d" % (day, delta_users, delta_bizs)

        # Step 2. 3. 4. Sample life time, link new nodes using PA, Sample wakeup time 
        
        print "Adding users"
        for _ in range(delta_users):
            datestr = date_start.strftime("%Y-%m-%d")
            new_nodeId = add_node(cst.ATTR_NODE_USER_TYPE, datestr)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_BUSINESS_TYPE)
            add_edge(new_nodeId, linked_nodeId, datestr) # TODO: step to change 

        print "Adding businesses"
        for _ in range(delta_bizs):
            datestr = date_start.strftime("%Y-%m-%d")
            new_nodeId = add_node(cst.ATTR_NODE_BUSINESS_TYPE, datestr)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_USER_TYPE)
            add_edge(linked_nodeId, new_nodeId, datestr) # TODO: step to change 

        print "Create links for wake up nodes"
        # Step 5. For wake up nodes, create link using random-random-random walk
        for nodeId, wakeuptime in nodewakeup.iteritems():
            if wakeuptime < day:
                linked_nodeId = get_random(graph, nodeId, 3) # 3 random!

        print "Die nodes."
        # Step 6. Remove nodes whose lifetime has expired
        for nodeId, litime in nodelifetime.iteritems():
            if lifetime < day:
                del nodewakeup[nodeId]

        nb_users += delta_users
        nb_bizs += delta_bizs
    
    return graph

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

