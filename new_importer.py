from generator import generateYelpReview, generateYelpUser, generateYelpBusiness

from snap import TNEANet, TFOut
import constants as cst

review_file = 'dataset/yelp_academic_dataset_review.json'
user_file = 'dataset/yelp_academic_dataset_user.json'
business_file = 'dataset/yelp_academic_dataset_business.json'
graph_file = 'computed/graph.bin'

states_of_interest = ['AZ','NV','EDH','WI','ON']
#states_of_interest = ['ON']

def generate_graph(business_filter):
    """Only businesses are filtered, then users linking to the businesses are loaded."""
    graph = TNEANet.New()
  
    # type of node
    graph.AddStrAttrN(cst.ATTR_NODE_ID)
    graph.AddStrAttrN(cst.ATTR_NODE_TYPE)
  
    # date when user started yelping
    graph.AddStrAttrN(cst.ATTR_NODE_CREATED_DATE)
    # adding elite year
    graph.AddIntAttrN(cst.ATTR_NODE_ELITE_YEAR)
  
    # proxy for business creation date (date of earliest review)
    graph.AddStrAttrE(cst.ATTR_EDGE_ID)
    graph.AddStrAttrE(cst.ATTR_EDGE_REVIEW_DATE)
  
    print('> Creating index')
    user_index_encid = dict()
    business_index_encid = dict()
  
    print('>> Creating business nodes')
    for business_encid, lng, lat, stars, state in generateYelpBusiness(business_file):
        if business_filter(state):
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
        if business_encid in business_index_encid:
            business_node_id = business_index_encid[business_encid]
  
            if user_encid in user_index_encid:
              user_node_id = user_index_encid[user_encid]
            else:
              user_node_id = graph.AddNode()
              user_index_encid[user_encid] = user_node_id
  
            
            edge = graph.AddEdge(user_node_id, business_node_id)
            graph.AddStrAttrDatE(edge, review_encid, cst.ATTR_EDGE_ID)
            graph.AddStrAttrDatE(edge, date, cst.ATTR_EDGE_REVIEW_DATE)
  
            # update opening_date if review creation precedes current estimate
            old_date = graph.GetStrAttrDatN(business_node_id, cst.ATTR_NODE_CREATED_DATE)
            if date < old_date:
                graph.AddStrAttrDatN(business_node_id, date, cst.ATTR_NODE_CREATED_DATE)
  
    print('>> Updating user nodes dates')
    for user_encid, date, elite in generateYelpUser(user_file):
        if user_encid in user_index_encid:
            user_node_id = user_index_encid[user_encid]

            # adding node type
            graph.AddStrAttrDatN(user_node_id, cst.ATTR_NODE_USER_TYPE, cst.ATTR_NODE_TYPE)

            # storing encID
            graph.AddStrAttrDatN(user_node_id, user_encid, cst.ATTR_NODE_ID)

            # elite status
            graph.AddIntAttrDatN(user_node_id, min(elite) if elite else cst.ATTR_NOT_ELITE, cst.ATTR_NODE_ELITE_YEAR)
  
            # add time when user joined
            graph.AddStrAttrDatN(user_node_id, date, cst.ATTR_NODE_CREATED_DATE)

    return graph

def import_states(states_of_interest=states_of_interest):
    for state_of_interest in states_of_interest:
        print('> '+state_of_interest)
        
        graph = generate_graph(lambda x: x == state_of_interest)
        
        graph_file = "computed/graph_elite_" + state_of_interest + ".bin"
        print('> Storing graph')
        f = TFOut(graph_file)
        graph.Save(f)
        graph.Clr()

def import_full():
    graph = generate_graph(lambda x: True)
    
    graph_file = "computed/graph_elite.bin"
    print('> Storing graph')
    f = TFOut(graph_file)
    graph.Save(f)
    graph.Clr()


