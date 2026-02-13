import json
import os
import boto3
from datetime import datetime

# Client AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment Variable
TABLE_NAME = os.environ.get('TABLE_NAME')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

# DynamoDB Table
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    try:
        # Loop semua pesan dari SQS
        for record in event['Records']:

            # Ambil pesan
            message = json.loads(record['body'])

            order_id = message['id']

            # Tambah timestamp
            message['timestamp'] = datetime.utcnow().isoformat()

            # Simpan ke DynamoDB
            table.put_item(
                Item=message
            )

            # Simpan ke S3 (backup/log)
            file_name = f"orders/{order_id}.json"

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
                Body=json.dumps(message),
                ContentType="application/json"
            )

            print(f"Order {order_id} berhasil diproses")

        return {
            "statusCode": 200,
            "body": "Success"
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise e
