from graphutils import copy_graph, delete_node_type, GetInOutEdges
import snap
from utils.disp import tempPrint

def projection(graph, attr='type', on_attr='user', using_attr='business'):
    proj_graph = copy_graph(graph)

    print('> Computing projection on %s using %s' % (on_attr, using_attr))
    nbnodes = proj_graph.GetNodes()

    for node in proj_graph.Nodes():
        node_id = node.GetId()
        node_type = proj_graph.GetStrAttrDatN(node_id, attr)
        if node_type == on_attr:
            nodeVec = snap.TIntV()
            snap.GetNodesAtHop(graph, node_id, 2, nodeVec, False)
            tempPrint('%d / %d' % (node_id, nbnodes))

            for next_neighbor_id in nodeVec:
                if proj_graph.GetStrAttrDatN(next_neighbor_id, attr) == on_attr and not proj_graph.IsEdge(node_id, next_neighbor_id): 
                    proj_graph.AddEdge(node_id, next_neighbor_id)

    delete_node_type(proj_graph, attr=attr, value=using_attr)
    return proj_graph

