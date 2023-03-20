import boto3
import random
import logging
import json
import requests
from requests_aws4auth import AWS4Auth

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initializing function...")


def lambda_handler(event, context):
    # Connect to AWS Services
    sqs = boto3.client("sqs")
    opensearch = boto3.client("opensearch")
    dynamodb = boto3.resource("dynamodb")
    sns = boto3.client("sns")

    # Loop through SQS queue items
    results = 0
    for record in event["Records"]:
        payload = record["body"]
        msg = json.loads(payload)

        # payload
        logger.info(msg)

        location = msg["Location"]
        cuisine_type = msg["Cuisine"]
        phone_number = msg["PhoneNumber"]

        results = search(cuisine_type)

        if "hits" not in results or "hits" not in results["hits"]:
            return {
                "statusCode": 200,
                "body": "No results found for the cuisine type: " + cuisine_type,
            }

        business_ids = [hit["id"] for hit in results["hits"]["hits"]]

        # Choose a random business ID from the list of IDs
        business_id = random.choice(business_ids)

        # Find more information (name and address) for the business ID in DynamoDB
        table = dynamodb.Table("yelp-restaurants-data")
        response = table.get_item(Key={"business_id": business_id})
        logger.info(response)

        if "Item" not in response:
            return {
                "statusCode": 200,
                "body": "No information found for the business ID: " + business_id,
            }
        item = response["Item"]

        # Send the SNS message with the recommendation
        sns.publish(
            PhoneNumber=phone_number,
            Message="Here is a restaurant recommendation based on your cuisine preference:\n\nName: {}\nAddress: {}".format(
                item["name"], item["address"]
            ),
        )

    return {"statusCode": 200, "body": "SNS message sent"}


def search(cuisine_type):
    region = "us-east-1"
    service = "es"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )

    host = "https://search-restaurants-phpxsplrypg7mascndh73x3uv4.us-east-1.es.amazonaws.com"
    index = "restaurants"
    url = host + "/" + index + "/_search"

    query = {
        "size": 25,
        "query": {"multi_match": {"query": cuisine_type, "fields": ["cuisineType"]}},
    }

    logger.info(query)

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = {"Content-Type": "application/json"}

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "isBase64Encoded": False,
    }
    result = r.text
    logger.info(result)

    return result
