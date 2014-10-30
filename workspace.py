import snap
from graphutils import delete_node_type, keep_edge_type, copy_graph
from projection import projection

graph_file = 'computed/graph.bin'

f = snap.TFIn(graph_file)
graph = snap.TNEANet.Load(f)

# print('> Projection on users')
# user_projection = projection(graph, on_attr='user', using_attr='business')
# print('%d Nodes left' % user_projection.GetNodes())
# print('%f Clusering coef' % snap.GetClustCf(user_projection))

# print('> Projection on businesses')
# business_projection = projection(graph, on_attr='business', using_attr='user')
# print('%d Nodes left' % business_projection.GetNodes())
# print('%f Clusering coef' % snap.GetClustCf(business_projection))


