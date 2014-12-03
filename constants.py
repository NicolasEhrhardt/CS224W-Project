# Node attributes
ATTR_NODE_ID = 'id'
ATTR_NODE_TYPE = 'type'
ATTR_NODE_CREATED_DATE = 'date'
ATTR_NODE_ELITE_YEAR = 'elite'

# All nodes attributes
ATTR_INT_NODE = {
    ATTR_NODE_ELITE_YEAR
}

ATTR_STR_NODE = {
    ATTR_NODE_ID,
    ATTR_NODE_TYPE,
    ATTR_NODE_CREATED_DATE,
}

# Attribute value for non elite
ATTR_NOT_ELITE = -1

# Attribute values for node types
ATTR_NODE_BUSINESS_TYPE = 'business'
ATTR_NODE_USER_TYPE = 'user'

# Default create date for businesses (first review is used as proxy)
DEFAULT_LATE_DATE = '2020-01-01'

# Edge attributes
ATTR_EDGE_ID = 'id'
ATTR_EDGE_REVIEW_DATE = 'date'

# All edge attributes
ATTR_STR_EDGE = {
    ATTR_EDGE_ID,
    ATTR_EDGE_REVIEW_DATE
}
