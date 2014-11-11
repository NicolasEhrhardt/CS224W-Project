import snap
from itertools import chain, tee
import constants as cst

def GetInOutEdges(self):
    """Return ids of In or Out Nodes"""
    return chain(self.GetOutEdges(), self.GetInEdges())

def get_sorted_edges_nodes(full_graph):
    print("> Sorting for computation")
    sortednodes = {}
    for node in full_graph.Nodes():
        nodeId = node.GetId()
        date = full_graph.GetStrAttrDatN(nodeId,cst.ATTR_NODE_CREATED_DATE)        
        
        if date not in sortednodes:
            sortednodes[date] = []
        
        sortednodes[date].append(nodeId)

    sortededges = {}
    for edge in full_graph.Edges():
        edgeId = edge.GetId()
        date = full_graph.GetStrAttrDatE(edgeId,cst.ATTR_EDGE_REVIEW_DATE)
        srcId = edge.GetSrcNId()
        dstId = edge.GetDstNId()
 
        if date not in sortededges:
            sortededges[date] = []

        sortededges[date].append((edgeId, srcId, dstId))

    return sortednodes, sortededges

def get_dates(min_year=2004, max_year=2014):
    # Creating dates array
    dates = ['']
    for year in range(min_year, max_year):
        for month in ['01','02','03','04','05','06','07','08','09','10','11','12']:
            date = str(year) + '-' + month + '-' + '01'
            dates.append(date)
    dates = dates[9::]
    dates.insert(0, '2000-01-01')
    return dates

def generate_all_generators(full_graph, max_year=2014,verbose=False):
    sortednodes, sortededges = get_sorted_edges_nodes(full_graph)
    dates = get_dates(max_year=max_year)

    for idate in range(1, len(dates)):
        # criterion of fetching only dates in the right month
        criterion = lambda x : x < dates[idate] and x >= dates[idate-1]
        # creating array of nodes and edges to go over
        curnodes = chain.from_iterable([sortednodes[k] for k in sortednodes if criterion(k)])
        curedges = chain.from_iterable([sortededges[k] for k in sortededges if criterion(k)])
        if verbose:
            print("> Yield edges and nodes until date %s" % dates[idate])
        yield curnodes, curedges, criterion

def generate_all_graphs(full_graph, detailed=False, max_year=2014):
    graph = get_empty_graph()
    for curnodes, curedges, criterion in generate_all_generators(full_graph, max_year):
        # updating graph
        if not detailed:
            users, busin = add_nodes_and_edges(full_graph, graph, criterion, curnodes=curnodes, curedges=curedges)
            yield users, busin, graph
        else:
            curnodes, curnodes_b = tee(curnodes)
            curedges, curedges_b = tee(curedges)
            users, busin = add_nodes_and_edges(full_graph, graph, criterion, curnodes=curnodes, curedges=curedges)
            yield users, busin, graph, curnodes_b, curedges_b

def delete_node_type(graph, attr='type', value='business'):
    """Delete all nodes of given type"""
    for node in graph.Nodes():
        node_id = node.GetId()
        if graph.GetStrAttrDatN(node_id, attr) == value:
            graph.DelNode(node_id)

def add_nodes_and_edges(full_graph, partial_graph, criterion=lambda x: x < '2010-01-01', curnodes=None, curedges=None):
    """ adds to partial_graph, nodes and edges from full_graph if they fulfill the criterion \
        returns a tuple containing (number of users added, number of businesses added)
    """

    users_added = 0 # number of users added to the graph
    busin_added = 0 # number of businesses added to the graph

    # node generator going over all the nodes or a subset if given
    def nodegen():
        if curnodes is None:
            for node in full_graph.Nodes():
                yield node.GetId()
        else:
            for x in curnodes:
                yield x

    # edge generator going voer all the edges or a subset if given
    def edgegen():
        if curedges is None:
            for edge in full_graph.Edges():
                srcId = edge.GetSrcNId()
                dstId = edge.GetDstNId()
                yield edge.GetId(), srcId, dstId
        else:
            for x in curedges:
                yield x

    for nodeId in nodegen():
        date = full_graph.GetStrAttrDatN(nodeId,cst.ATTR_NODE_CREATED_DATE)        
        if criterion(date) and not partial_graph.IsNode(nodeId):
            new_node = partial_graph.AddNode(nodeId)
            node_type = full_graph.GetStrAttrDatN(nodeId,cst.ATTR_NODE_TYPE)
            users_added += (node_type == cst.ATTR_NODE_USER_TYPE)
            busin_added += (node_type == cst.ATTR_NODE_BUSINESS_TYPE)
            partial_graph.AddStrAttrDatN(new_node,node_type,cst.ATTR_NODE_TYPE)
            partial_graph.AddStrAttrDatN(new_node,date,cst.ATTR_NODE_CREATED_DATE)
        elif curnodes is not None:
            print "Node not created", nodeId

    for edgeId, srcId, dstId in edgegen():
        date = full_graph.GetStrAttrDatE(edgeId,cst.ATTR_EDGE_REVIEW_DATE)
        if criterion(date) and partial_graph.IsNode(srcId) and partial_graph.IsNode(dstId) \
            and not partial_graph.IsEdge(srcId,dstId):

            new_edge = partial_graph.AddEdge(srcId, dstId)
            partial_graph.AddStrAttrDatE(new_edge,date,cst.ATTR_EDGE_REVIEW_DATE)
        elif curedges is not None and not (criterion(date) and partial_graph.IsNode(srcId) and partial_graph.IsNode(dstId)):
            print "Edge not created for weird reason", edgeId 

    return (users_added,busin_added)

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
