import json
import boto3
import uuid
import logging

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("Initializing function...")


def lambda_handler(event, context):
    logger.info(event)

    # Extract the text message from the API request
    message = event["messages"][0]["unstructured"]["text"]

    logger.info("Message received: " + message)

    # Connect to Lex
    lex_client = boto3.client("lexv2-runtime")

    # Generate a unique ID for the user
    user_id = str(uuid.uuid4())

    # Send the message to the Lex
    response = lex_client.recognize_text(
        botId="FCAA4FXHJO",
        botAliasId="NMFIB45KI3",
        localeId="en_US",
        sessionId=user_id,
        text=message,
        sessionState={},
    )

    logger.info(response)

    messages = []

    if "messages" in response:
        for message in response["messages"]:
            messages.append(
                {"type": "unstructured", "unstructured": {"text": message["content"]}}
            )

    # Return the response from Lex as the API response
    return {"statusCode": 200, "messages": messages}
