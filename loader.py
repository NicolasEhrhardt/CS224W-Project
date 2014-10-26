from generator import generateYelpReview
import snap

review_file = 'dataset/yelp_academic_dataset_review.json'
graph_file = 'data/graph.bin'

graph = snap.TNEANet.New()
#graph.AddIntAttrN('type')
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
        graph.AddIntAttrDatN(user_node_id, 0, 'type')
        user_index_encid[user_encid] = user_node_id
    else:
        user_node_id = user_index_encid[user_encid]
    
    business_node_id = -1
    if business_encid not in business_index_encid:
        business_node_id = graph.AddNode()
        graph.AddIntAttrDatN(business_node_id, 1, 'type')
        business_index_encid[business_encid] = business_node_id
    else:
        business_node_id = business_index_encid[business_encid]

    edge = graph.AddEdge(user_node_id, business_node_id)
    graph.AddStrAttrDatE(edge, date, 'date')

print('Storing graph')
f = snap.TFOut(graph_file)
graph.Save(f)

