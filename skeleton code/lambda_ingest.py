import json
import boto3
import os

sqs = boto3.client('sqs')
QUEUE_URL = os.environ['SQS_URL']

def lambda_handler(event, context):

    body = {}

    if 'body' in event and event['body']:
        try:
            body = json.loads(event['body'])
        except:
            body = {}

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(body)
    )

    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "status": "success",
            "message": "Order masuk ke queue"
        })
    }
