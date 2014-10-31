from generator import generateYelpReview, generateYelpUser, generateYelpBusiness
from snap import TNEANet, TFOut
import constants as cst

review_file = 'dataset/yelp_academic_dataset_review.json'
user_file = 'dataset/yelp_academic_dataset_user.json'
business_file = 'dataset/yelp_academic_dataset_business.json'
graph_file = 'computed/graph.bin'

graph = TNEANet.New()

# type of node
graph.AddStrAttrN(cst.ATTR_NODE_ID)
graph.AddStrAttrN(cst.ATTR_NODE_TYPE)

# date when user started yelping
graph.AddStrAttrN(cst.ATTR_NODE_CREATED_DATE)

# proxy for business creation date (date of earliest review)
graph.AddStrAttrE(cst.ATTR_EDGE_ID)
graph.AddStrAttrE(cst.ATTR_EDGE_REVIEW_DATE)

graph.Reserve(300000, 1200000)

print('> Creating index')
dates = dict()
user_index_encid = dict()
business_index_encid = dict()
business_date = dict()

print('>> Creating user nodes')
for user_encid, date in generateYelpUser(user_file):
    user_node_id = graph.AddNode()
    graph.AddStrAttrDatN(user_node_id, user_encid, cst.ATTR_NODE_ID)
    graph.AddStrAttrDatN(user_node_id, cst.ATTR_NODE_USER_TYPE, cst.ATTR_NODE_TYPE)
    user_index_encid[user_encid] = user_node_id

    # add time when user joined
    graph.AddStrAttrDatN(user_node_id, date, cst.ATTR_NODE_CREATED_DATE)


print('>> Creating business nodes')
for business_encid, lng, lat, stars in generateYelpBusiness(business_file):
    business_node_id = graph.AddNode()
    graph.AddStrAttrDatN(business_node_id, business_encid, cst.ATTR_NODE_ID)
    graph.AddStrAttrDatN(business_node_id, cst.ATTR_NODE_BUSINESS_TYPE, cst.ATTR_NODE_TYPE)
    business_index_encid[business_encid] = business_node_id

    # add time when user joined
    graph.AddStrAttrDatN(business_node_id, cst.DEFAULT_LATE_DATE, cst.ATTR_NODE_CREATED_DATE)

print('>> Creating review edges')
for review_encid, user_encid, business_encid, date in generateYelpReview(review_file):
    if date == '':
        print 'reviewid: %s has no date' % review_encid

    user_node_id = user_index_encid[user_encid]
    business_node_id = business_index_encid[business_encid]

    edge = graph.AddEdge(user_node_id, business_node_id)
    graph.AddStrAttrDatE(edge, review_encid, cst.ATTR_EDGE_ID)
    graph.AddStrAttrDatE(edge, date, cst.ATTR_EDGE_REVIEW_DATE)

    # update opening_date if review creation precedes current estimate
    old_date = graph.GetStrAttrDatN(business_node_id, cst.ATTR_NODE_CREATED_DATE)
    if date < old_date:
        graph.AddStrAttrDatN(business_node_id, date, cst.ATTR_NODE_CREATED_DATE)

print('> Storing graph')
f = TFOut(graph_file)
graph.Save(f)
