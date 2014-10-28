from generator import generateYelpReview
from snap import TNEANet, TFOut

review_file = 'dataset/yelp_academic_dataset_review.json'
graph_file = 'computed/graph.bin'

graph = TNEANet.New()
graph.AddStrAttrN('type')
graph.AddStrAttrE('date')
graph.Reserve(300000, 1200000)

print('> Creating index')
dates = dict()
user_index_encid = dict()
business_index_encid = dict()
for user_encid, business_encid, date in generateYelpReview(review_file):
    user_node_id = -1
    if user_encid not in user_index_encid:
        user_node_id = graph.AddNode()
        graph.AddStrAttrDatN(user_node_id, 'user', 'type')
        user_index_encid[user_encid] = user_node_id
    else:
        user_node_id = user_index_encid[user_encid]
    
    business_node_id = -1
    if business_encid not in business_index_encid:
        business_node_id = graph.AddNode()
        graph.AddStrAttrDatN(business_node_id, 'business', 'type')
        business_index_encid[business_encid] = business_node_id
    else:
        business_node_id = business_index_encid[business_encid]

    edge = graph.AddEdge(user_node_id, business_node_id)
    graph.AddStrAttrDatE(edge, date, 'date')

print('> Storing graph')
f = TFOut(graph_file)
graph.Save(f)
graph.Clr()
