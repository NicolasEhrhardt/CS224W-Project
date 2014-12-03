from graphutils import get_empty_graph, add_nodes_and_edges
from random import sample
import constants as cst

def get_half(graph, cut=lambda x: x < '2011-01-01'):
    half_graph = get_empty_graph()
    add_nodes_and_edges(graph, half_graph, cut)
    return half_graph

def simulate(graph, userarrival, bizarrival, lifetime, reviewdelta, nstep=10):
    nodelifetime = dict()
    nodewakeup = dict()

    for node in graph.Nodes():
        if graph.GetStrAttrDatN(node.GetId(), cst.ATTR_NODE_TYPE) == cst.ATTR_NODE_USER_TYPE:
            nodelifetime[node.GetId()] = lifetime()
            nodewakeup[node.GetId()] = reviewdelta()

    def add_node(node_type):
        # adding node and metadata
        new_nodeId = graph.AddNode()
        graph.AddStrAttrDatN(new_nodeId, node_type)

        if node_type == cst.ATTR_NODE_USER_TYPE:
            # set lifetime and wake-up time
            nodelifetime[new_nodeId] = lifetime()
            nodewakeup[new_nodeId] = reviewdelta()

        return new_nodeId

    def add_edge(srcId, dstId, date):
        edgeId = graph.AddEdge(srcId, dstId)
        graph.AddStrAttrDatE(edgeId, date, cst.ATTR_EDGE_REVIEW_DATE)
        return edgeId

    for step in range(nstep):
        
        # Step 1. Add new nodes

        nb_newusers = userarrival(step)
        nb_newbizs = bizarrival(step)

        # Step 2. 3. 4. Sample life time, link new nodes using PA, Sample wakeup time 

        for _ in range(nb_newusers):
            new_nodeId = add_node(cst.ATTR_NODE_USER_TYPE)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_BUSINESS_TYPE)
            add_edge(new_nodeId, linked_nodeId, step) # TODO: step to change 

        for _ in range(nb_newbizs):
            new_nodeId = add_node(cst.ATTR_NODE_BUSINESS_TYPE)
            linked_nodeId = get_PA(graph, cst.ATTR_NODE_USER_TYPE)
            add_edge(linked_nodeId, new_nodeId, step) # TODO: step to change 

        # Step 5. For wake up nodes, create link using random-random-random walk
        for nodeId, wakeuptime in nodewakeup.iteritems():
            if wakeuptime < step:
                linked_nodeId = get_random(graph, nodeId, 3) # 3 random!

        # Step 6. Remove nodes whose lifetime has expired
        for nodeId, lifetime in nodelifetime.iteritems():
            if lifetime < step:
                del nodewakeup[nodeId]

def get_PA(graph, node_type):
    node = graph.GetRndNI()
    while graph.GetStrAttrDatN(node.GetId(), cst.ATTR_NODE_TYPE) != node_type:
        node = graph.GetRndNI()

    neighborIds = [neighborId for neighborId in node.GetOutEdges()]
    return sample(neighborIds)

def get_random(graph, nodeId, jump):
    if jump == 0:
        return nodeId
    
    node = graph.GetNI(nodeId)
    neighborIds = [neighborId for neighborId in node.GetOutEdges()]

    return get_random(graph, sample(neighborIds), jump - 1)

