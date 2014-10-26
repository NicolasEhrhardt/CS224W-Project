from utils import data
import json

def generateYelpReview(filename):
    # extracting tokens
    for line in data.generateLine(filename):
        review = json.loads(line)
        user_id = review['user_id']
        business_id = review['business_id']
        date = review['date']
        yield user_id, business_id, date

def generateYelpUser(filename):
    # extracting tokens
    for line in data.generateLine(filename):
        user = json.loads(line)
        user_id = user['user_id']
        date = user['yelping_since']
        yield user_id, date
