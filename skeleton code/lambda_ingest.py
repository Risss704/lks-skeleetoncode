import json
import os
import boto3
import uuid

# Client SQS
sqs = boto3.client('sqs')

# Ambil URL Queue dari Environment Variable
SQS_URL = os.environ.get('SQS_URL')


def lambda_handler(event, context):

    try:
        # Ambil data dari request ALB
        if "body" in event and event["body"]:
            body = json.loads(event["body"])
        else:
            body = {}

        # Buat ID unik order
        order_id = str(uuid.uuid4())

        # Data pesanan
        order_data = {
            "id": order_id,
            "name": body.get("name", "unknown"),
            "product": body.get("product", "unknown"),
            "quantity": body.get("quantity", 1)
        }

        # Kirim ke SQS
        sqs.send_message(
            QueueUrl=SQS_URL,
            MessageBody=json.dumps(order_data)
        )

        # Response ke client
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Order berhasil diterima",
                "order_id": order_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
