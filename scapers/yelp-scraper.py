import boto3
import requests
import json
import time
from datetime import datetime
from decimal import Decimal
import os

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Replace API_KEY with your own Yelp Fusion API key
API_KEY = "*"
# Base URL for the Yelp Fusion API
BASE_URL = "https://api.yelp.com/v3/businesses/search"

# Search parameters
location = "Manhattan, NY"
term = "restaurant"

# API request headers
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Connect to the DynamoDB table
dynamodb = boto3.resource("dynamodb", 
         aws_access_key_id='*',
         aws_secret_access_key='*')
table = dynamodb.Table("yelp-restaurant-data")

# Keep track of the total number of restaurants returned by the API
total_restaurants = 0

# Keep track of the number of API requests made
api_requests = 0

# Keep looping until all restaurants have been retrieved
business_id_set = set()

offset = 0
categories = ["German","French", "chinese","indian","korean","japanese","italian"]
for category in categories:
    while True:
        # Make an API request
        params = {
            "term": term,
            "location": location,
            "categories": category,
            "limit": 50,  # Number of results to return per API request
            "offset": offset
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        # Raise an error if the API request was unsuccessful
        try:
            response.raise_for_status()
        except Exception as e:
            print("WE have exception e: ", e)
            time.sleep(5)
            continue

        # Parse the JSON response
        data = json.loads(response.text)

        # Get the list of restaurants from the API response
        restaurants = data["businesses"]

        # Update the total number of restaurants
        total_restaurants += len(restaurants)
        if offset >= 950:
            offset = 0
            break
        # Loop through each restaurant
        with open("yelp_opensearch.json", "a") as f:
            for restaurant in restaurants:
                # Get the restaurant information
                business_id = restaurant["id"]
                cuisine = restaurant["categories"][0]["title"]
                if business_id in business_id_set:
                    continue
                business_id_set.add(business_id)
                name = restaurant["name"]
                address = restaurant["location"]["address1"]
                latitude = Decimal(str(restaurant["coordinates"]["latitude"]))
                longitude = Decimal(str(restaurant["coordinates"]["longitude"]))
                review_count = int(restaurant["review_count"])
                rating = Decimal(str(restaurant["rating"]))
                zip_code = restaurant["location"]["zip_code"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + str(int(datetime.now().microsecond / 1000)).zfill(3)
                table.put_item(
                    Item={
                        "insertedAtTimestamp": timestamp,
                        "businessId": business_id,
                        "cuisine": cuisine,
                        "name": name,
                        "address": address,
                        "latitude": latitude,
                        "longitude": longitude,
                        "reviewCount": review_count,
                        "rating": rating,
                        "zipCode": zip_code
                    }
                )
                if cuisine != None and business_id != None:
                    f.write('{"index":{}}\n{"restaurantID":"')
                    f.write(business_id)
                    f.write('", "Cuisine":"')
                    f.write(cuisine)
                    f.write('"}\n')
        offset += 50
        if len(business_id_set) >= 5000:
            break
