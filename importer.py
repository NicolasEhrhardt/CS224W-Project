from generator import generateYelpReview, generateYelpUser, generateYelpBusiness
from snap import TNEANet, TFOut

ATTR_NODE_TYPE = 'type'

ATTR_NODE_BUSINESS_TYPE = 'business'
ATTR_NODE_BUSINESS_OPENING_DATE = 'date'

ATTR_NODE_USER_TYPE = 'user'
ATTR_NODE_USER_JOINING_DATE = 'date'

ATTR_EDGE_REVIEW_DATE = 'date'
DEFAULT_EARLY_DATE = '2000-01-01'

review_file = 'dataset/yelp_academic_dataset_review.json'
user_file = 'dataset/yelp_academic_dataset_user.json'
business_file = 'dataset/yelp_academic_dataset_business.json'
graph_file = 'computed/graph.bin'

graph = TNEANet.New()
graph.AddStrAttrN('type')

# date when user started yelping
graph.AddStrAttrN(ATTR_NODE_USER_JOINING_DATE)

# proxy for business creation date (date of earliest review)
graph.AddStrAttrN(ATTR_NODE_BUSINESS_OPENING_DATE)
graph.AddStrAttrE('date')
graph.Reserve(300000, 1200000)

print('> Creating index')
dates = dict()
user_index_encid = dict()
business_index_encid = dict()


print('>> Creating user nodes')
for user_encid, date in generateYelpUser(user_file):
    user_node_id = graph.AddNode()
    graph.AddStrAttrDatN(user_node_id, ATTR_NODE_USER_TYPE, ATTR_NODE_TYPE)
    user_index_encid[user_encid] = user_node_id

    # add time when user joined
    graph.AddStrAttrDatN(user_node_id, date, ATTR_NODE_USER_JOINING_DATE)


print('>> Creating business nodes')
for business_encid, lng, lat, stars in generateYelpBusiness(business_file):
    business_node_id = graph.AddNode()
    graph.AddStrAttrDatN(business_node_id, ATTR_NODE_BUSINESS_TYPE, ATTR_NODE_TYPE)
    business_index_encid[business_encid] = business_node_id

    # add time when user joined
    graph.AddStrAttrDatN(user_node_id, DEFAULT_EARLY_DATE, ATTR_NODE_BUSINESS_OPENING_DATE)

print('>> Creating review edges')
for user_encid, business_encid, date in generateYelpReview(review_file):
    user_node_id = user_index_encid[user_encid]
    business_node_id = business_index_encid[business_encid]

    edge = graph.AddEdge(user_node_id, business_node_id)
    graph.AddStrAttrDatE(edge, date, ATTR_EDGE_REVIEW_DATE)

    # update opening_date if review creation precedes current estimate
    old_date = graph.GetStrAttrDatN(business_node_id, ATTR_NODE_BUSINESS_OPENING_DATE)
    if date < old_date:
        graph.AddStrAttrDatN(business_node_id,date,ATTR_NODE_BUSINESS_OPENING_DATE)

print('> Storing graph')
f = TFOut(graph_file)
graph.Save(f)
