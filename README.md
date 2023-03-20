# Dining Suggestion Chatbot

This project demonstrates an end-to-end serverless application that utilizes AWS Lambda, Amazon Lex, Amazon SQS, Amazon OpenSearch, DynamoDB, and Amazon SNS to provide dining suggestions based on users' preferences.

## Overview

1. Users interact with the Amazon Lex chatbot via a text-based interface.
2. The Lambda function processes user input and responds accordingly, handling intents like greetings, thank yous, and dining suggestions.
3. For dining suggestions, the Lambda function stores the user's preferences in an Amazon SQS queue.
4. Another Lambda function processes the SQS queue, searches for matching restaurants using Amazon OpenSearch, and sends a recommended restaurant to the user via an Amazon SNS message.

## Prerequisites

- AWS account with access to Lambda, Lex, SQS, OpenSearch, DynamoDB, and SNS
- Python 3.x
- AWS CLI
- AWS SAM CLI (Serverless Application Model)
- Yelp dataset stored in DynamoDB (with restaurants indexed in Amazon OpenSearch)

## Setup and Deployment

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/dining-suggestion-chatbot.git
cd dining-suggestion-chatbot
```
### 2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Configure AWS credentials
```bash
aws configure 
```
### 4. Create an Amazon Lex chatbot
Follow the Amazon Lex documentation to create a chatbot with the intents and slots used in the Lambda functions.

### 5. Deploy the Lambda functions
Use the AWS SAM CLI to package and deploy the Lambda functions.
```bash
sam build
sam deploy --guided
```
### 6. Update the Amazon Lex chatbot Lambda integration
Update the Amazon Lex chatbot to use the deployed Lambda function for processing intents.

### 7. Create an Amazon SQS queue
Create an Amazon SQS queue to store user preferences for dining suggestions. Update the Lambda functions with the appropriate queue URL.

### 8. Populate DynamoDB and Amazon OpenSearch with restaurant data
Ensure the Yelp dataset is stored in DynamoDB and indexed in Amazon OpenSearch. Update the Lambda functions with the appropriate OpenSearch and DynamoDB configurations.

## Usage 
Interact with the Amazon Lex chatbot via the text-based interface. The chatbot will respond to greetings, thank yous, and provide dining suggestions based on user preferences.

## License 
This project is licensed under the MIT License. See the LICENSE file for details.

