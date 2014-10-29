from generator import generateYelpReview
from datetime import datetime
from snap import TNEANet, TFOut

ATTR_NODE_TYPE = 'type'
ATTR_JOINING_DATE = 'date'
ATTR_OPENING_DATE = 'date'
DATE_FORMAT = '%Y-%m-%d'

review_file = 'dataset/yelp_academic_dataset_review.json'
graph_file = 'computed/graph.bin'

graph = TNEANet.New()
graph.AddStrAttrN('type')

# date when user started yelping
graph.AddStrAttrN(ATTR_JOINING_DATE)

# proxy for business creation date (date of earliest review)
graph.AddStrAttrN(ATTR_OPENING_DATE)
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

        # add time when user joined
        graph.AddStrAttrDatN(user_node_id,date,ATTR_JOINING_DATE)
    else:
        user_node_id = user_index_encid[user_encid]
    
    business_node_id = -1
    if business_encid not in business_index_encid:
        business_node_id = graph.AddNode()
        graph.AddStrAttrDatN(business_node_id, 'business', 'type')
        business_index_encid[business_encid] = business_node_id
        # temporarily add current review creation as date
        graph.AddStrAttrDatN(business_node_id,date,ATTR_OPENING_DATE)

    else:
        business_node_id = business_index_encid[business_encid]
        # update opening_date if review creation precedes current estimate
        old_date = graph.GetStrAttrDatN(business_node_id,ATTR_OPENING_DATE)
        if date < old_date:
            graph.AddStrAttrDatN(business_node_id,date,ATTR_OPENING_DATE)
    
    edge = graph.AddEdge(user_node_id, business_node_id)
    graph.AddStrAttrDatE(edge, date, 'date')

print('> Storing graph')
f = TFOut(graph_file)
graph.Save(f)
#graph.Clr()
