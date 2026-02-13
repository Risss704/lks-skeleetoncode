from flask import Flask, jsonify
import boto3
import os

# =============================
# EDIT SESUAI NOMOR PESERTA
# =============================
NOMOR_PESERTA = "XX"


# =============================
# CONFIG
# =============================
REGION = "us-east-1"

VPC_NAME = f"LKS26-VPC-{NOMOR_PESERTA}"
QUEUE_NAME = f"LKS26-Queue-Orders-{NOMOR_PESERTA}"
TABLE_NAME = f"LKS26-Orders-{NOMOR_PESERTA}"
ALB_NAME = f"LKS26-ALB-{NOMOR_PESERTA}"


# =============================
# AWS CLIENT
# =============================
ec2 = boto3.client("ec2", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.client("dynamodb", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)


app = Flask(__name__)


# =============================
# CEK VPC
# =============================
def check_vpc():
    vpcs = ec2.describe_vpcs()

    for vpc in vpcs["Vpcs"]:
        for tag in vpc.get("Tags", []):
            if tag["Key"] == "Name" and tag["Value"] == VPC_NAME:
                return True

    return False


# =============================
# CEK SQS
# =============================
def check_sqs():
    queues = sqs.list_queues()

    for url in queues.get("QueueUrls", []):
        if QUEUE_NAME in url:
            return True

    return False


# =============================
# CEK DYNAMODB
# =============================
def check_dynamodb():
    tables = dynamodb.list_tables()

    if TABLE_NAME in tables["TableNames"]:
        return True

    return False


# =============================
# CEK ALB
# =============================
def check_alb():
    lbs = elbv2.describe_load_balancers()

    for lb in lbs["LoadBalancers"]:
        if lb["LoadBalancerName"] == ALB_NAME:
            return True

    return False


# =============================
# API STATUS
# =============================
@app.route("/", methods=["GET"])
def status():

    result = {
        "peserta": NOMOR_PESERTA,
        "region": REGION,
        "vpc": check_vpc(),
        "sqs": check_sqs(),
        "dynamodb": check_dynamodb(),
        "alb": check_alb()
    }

    return jsonify(result)


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
