from utils import data
import json

def generateYelpReview(filename):
    # extracting tokens
    for line in data.generateLine(filename):
        review = json.loads(line)
        review_id = review['review_id']
        user_id = review['user_id']
        business_id = review['business_id']
        date = review['date']
        yield review_id, user_id, business_id, date

def generateYelpUser(filename):
    # extracting tokens
    for line in data.generateLine(filename):
        user = json.loads(line)
        user_id = user['user_id']
        date = user['yelping_since']
        elite = user['elite']
        yield user_id, date, elite

def generateYelpBusiness(filename):
    # extracting tokens
    for line in data.generateLine(filename):
        business = json.loads(line)
        business_id = business['business_id']
        lng, lat = business['longitude'], business['latitude']
        stars = business['stars']
        state = business['state']
        yield business_id, lng, lat, stars,state.strip()
