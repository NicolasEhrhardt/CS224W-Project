from graphutils import get_empty_graph, add_nodes_and_edges

def get_half(graph, cut=lambda x: x < '2011-01-01'):
    half_graph = get_empty_graph()
    add_nodes_and_edges(graph, half_graph, cut)
    return half_graph
