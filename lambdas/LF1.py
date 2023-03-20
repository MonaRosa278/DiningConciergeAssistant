import boto3
import json
import logging

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initializing function...")

sqs = boto3.client("sqs")
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/636958802040/MessageQ"


def lambda_handler(event, context):

    logger.info(event)

    current_intent = event["sessionState"]["intent"]
    intent_name = current_intent["name"]

    session_attributes = {}
    active_contexts = {}
    session_attributes["sessionId"] = event["sessionId"]

    logger.info("Intent name: " + intent_name)

    slots = current_intent["slots"]
    logger.info(slots)

    if intent_name == "GreetingIntent":
        current_intent["state"] = "Fulfilled"
        return close(
            session_attributes,
            active_contexts,
            "Fulfilled",
            current_intent,
            "Hello! How can I help you today?",
        )

    elif intent_name == "ThankYouIntent":
        current_intent["state"] = "Fulfilled"
        return close(
            session_attributes,
            active_contexts,
            "Fulfilled",
            current_intent,
            "You're welcome. Have a great day!",
        )

    elif intent_name == "DiningSuggestionIntent":

        location = (
            slots["Location"]["value"]["interpretedValue"]
            if slots["Location"] is not None and "value" in slots["Location"]
            else None
        )
        cuisine = (
            slots["Cuisine"]["value"]["interpretedValue"]
            if "value" in slots["Cuisine"]
            else None
        )
        dining_time = (
            slots["DiningTime"]["value"]["interpretedValue"]
            if slots["DiningTime"] is not None and "value" in slots["DiningTime"]
            else None
        )
        number_of_people = (
            slots["NumberOfPeople"]["value"]["interpretedValue"]
            if slots["NumberOfPeople"] is not None
            and "value" in slots["NumberOfPeople"]
            else None
        )
        phone_number = (
            slots["PhoneNumber"]["value"]["interpretedValue"]
            if slots["PhoneNumber"] is not None and "value" in slots["PhoneNumber"]
            else None
        )

        payload = {
            "Location": location,
            "Cuisine": cuisine,
            "DiningTime": dining_time,
            "NumberOfPeople": number_of_people,
            "PhoneNumber": phone_number,
        }

        logger.info("Sending payload to SQS:")
        logger.info(payload)

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload),
        )

        current_intent["state"] = "Fulfilled"
        return close(
            session_attributes,
            active_contexts,
            "Fulfilled",
            current_intent,
            "Thank you for your request. We have received your information and will notify you over SMS with a list of restaurant suggestions.",
        )


def close(session_attributes, active_contexts, fulfillment_state, intent, message):
    response = {
        "sessionState": {
            "activeContexts": [
                {
                    "name": "intentContext",
                    "contextAttributes": active_contexts,
                    "timeToLive": {"timeToLiveInSeconds": 600, "turnsToLive": 1},
                }
            ],
            "sessionAttributes": session_attributes,
            "dialogAction": {
                "type": "Close",
            },
            "intent": intent,
        },
        "messages": [{"contentType": "PlainText", "content": message}],
    }

    return response
