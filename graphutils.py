import snap
import itertools
import constants as cst

def GetInOutEdges(self):
    """Return ids of In or Out Nodes"""
    return itertools.chain(self.GetOutEdges(), self.GetInEdges())

def delete_node_type(graph, attr='type', value='business'):
    """Delete all nodes of given type"""
    for node in graph.Nodes():
        node_id = node.GetId()
        if graph.GetStrAttrDatN(node_id, attr) == value:
            graph.DelNode(node_id)

def add_nodes_and_edges(full_graph, partial_graph, criterion=lambda x: x < '2010-01-01'):
    """ adds to partial_graph, nodes and edges from full_graph if they fulfill the criterion """

    for node in full_graph.Nodes():
        nodeId = node.GetId()
        date = full_graph.GetStrAttrDatN(nodeId,cst.ATTR_NODE_CREATED_DATE)
        if criterion(date) and not partial_graph.IsNode(nodeId):
            new_node = partial_graph.AddNode(nodeId)
            node_type = full_graph.GetStrAttrDatN(nodeId,cst.ATTR_NODE_TYPE)
            partial_graph.AddStrAttrDatN(new_node,node_type,cst.ATTR_NODE_TYPE)
            partial_graph.AddStrAttrDatN(new_node,date,cst.ATTR_NODE_CREATED_DATE)

    for edge in full_graph.Edges():
        date = full_graph.GetStrAttrDatE(edge.GetId(),cst.ATTR_EDGE_REVIEW_DATE)
        srcId = edge.GetSrcNId()
        dstId = edge.GetDstNId()
        if criterion(date) and partial_graph.IsNode(srcId) and partial_graph.IsNode(dstId) \
            and not partial_graph.IsEdge(srcId,dstId):

            new_edge = partial_graph.AddEdge(edge.GetSrcNId(), edge.GetDstNId())
            partial_graph.AddStrAttrDatE(new_edge,date,cst.ATTR_EDGE_REVIEW_DATE)

def get_empty_graph():
     
    ng = snap.TNEANet.New()
    ng.AddStrAttrN(cst.ATTR_NODE_TYPE)
    ng.AddStrAttrN(cst.ATTR_NODE_ID)
    ng.AddStrAttrE(cst.ATTR_EDGE_REVIEW_DATE)
    ng.AddStrAttrE(cst.ATTR_EDGE_ID)

    return ng

def get_subgraph_by_date(graph, criterion=lambda x: x < '2010-01-01'):
    """Returns new graph with edges and nodes matching value boolean lambda function"""
    ng = snap.TNEANet.New()
    ng.AddStrAttrN(cst.ATTR_NODE_TYPE)
    ng.AddStrAttrN(cst.ATTR_NODE_ID)
    ng.AddStrAttrE(cst.ATTR_EDGE_REVIEW_DATE)
    ng.AddStrAttrE(cst.ATTR_EDGE_ID)
    add_nodes_and_edges(graph, ng, criterion)
    
    return ng

def copy_graph(graph):
    """Returns a copy of the graph (~5s copy)"""
    tmpfile = '.copy.bin'

    # Saving to tmp file
    FOut = snap.TFOut(tmpfile)
    graph.Save(FOut)
    FOut.Flush()

    # Loading to new graph
    FIn = snap.TFIn(tmpfile)
    graphtype = type(graph)
    new_graph = graphtype.New()
    new_graph = new_graph.Load(FIn)
    
    return new_graph

# ~ Ignore Below ~

def failing_keep_edge_type(graph, attr='date', value=lambda x: x < '2010-01-01' ):
    for edge in snap.Edges(graph):
        edge_id = edge.GetId()
        if value(graph.GetStrAttrDatE(edge_id, attr)):
            graph.DelAttrDatE(edge_id, attr)
            # this thing under does not work...?!
            graph.DelEdge(edge.GetSrcNId(), edge.GetDstNId())


def inefficient_copy_graph(graph, node_str_attrs=['type'], edge_str_attrs=['date']):
    graphtype = type(graph)
    new_graph = graphtype.New()
    new_graph.Reserve(graph.GetNodes(), graph.GetEdges())
   
    for node in graph.Nodes():
        node_id = node.GetId()
        new_graph.AddNode(node_id)
        if graphtype.__name__ == 'PNEANet':
            for node_str_attr in node_str_attrs:
                new_graph.AddStrAttrDatN(node_id, graph.GetStrAttrDatN(node_id, node_str_attr), node_str_attr)

    for edge in graph.Edges():
        edge_id = edge.GetId()
        new_edge_id = new_graph.AddEdge(edge.GetSrcNId(), edge.GetDstNId())
        #new_edge_id = new_edge.GetId()
        if graphtype.__name__ == 'PNEANet':
            for edge_str_attr in edge_str_attrs:
                new_graph.AddStrAttrDatE(new_edge_id, graph.GetStrAttrDatE(edge_id, edge_str_attr), edge_str_attr)

    return new_graph
