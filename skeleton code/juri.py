import boto3

XX = "01"   # GANTI nomor peserta

REGION = "us-east-1"

ec2 = boto3.client("ec2", region_name=REGION)
ddb = boto3.client("dynamodb", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
sqs = boto3.client("sqs", region_name=REGION)
lam = boto3.client("lambda", region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)


def ok(msg):
    print("[OK]  ", msg)


def fail(msg):
    print("[FAIL]", msg)


print("\n=== AUTO CHECK LKS CLOUD 2026 ===\n")


# =====================
# VPC
# =====================
vpcs = ec2.describe_vpcs()

vpc_id = None

for v in vpcs["Vpcs"]:
    if v["CidrBlock"] == "10.0.0.0/16":
        vpc_id = v["VpcId"]
        ok("VPC CIDR benar")
        break

if not vpc_id:
    fail("VPC CIDR tidak ditemukan")


# =====================
# Subnet
# =====================
subs = ec2.describe_subnets(Filters=[
    {"Name": "vpc-id", "Values": [vpc_id]}
])

subnet_map = {}

for s in subs["Subnets"]:
    subnet_map[s["CidrBlock"]] = s["SubnetId"]

needed = [
    "10.0.1.0/24",
    "10.0.2.0/24",
    "10.0.3.0/24",
    "10.0.4.0/24"
]

for cidr in needed:
    if cidr in subnet_map:
        ok(f"Subnet {cidr}")
    else:
        fail(f"Subnet {cidr}")


# =====================
# VPC Endpoint
# =====================
eps = ec2.describe_vpc_endpoints()

services = []

for e in eps["VpcEndpoints"]:
    services.append(e["ServiceName"])

if "com.amazonaws.us-east-1.s3" in services:
    ok("Endpoint S3")

else:
    fail("Endpoint S3")

if "com.amazonaws.us-east-1.dynamodb" in services:
    ok("Endpoint DynamoDB")

else:
    fail("Endpoint DynamoDB")

if "com.amazonaws.us-east-1.sqs" in services:
    ok("Endpoint SQS")

else:
    fail("Endpoint SQS")


# =====================
# DynamoDB
# =====================
try:
    tables = ddb.list_tables()["TableNames"]

    if f"LKS26-Orders-{XX}" in tables:
        ok("DynamoDB Table")
    else:
        fail("DynamoDB Table")

except:
    fail("DynamoDB Error")


# =====================
# S3
# =====================
try:
    buckets = s3.list_buckets()["Buckets"]

    found = False

    for b in buckets:
        if b["Name"] == f"lks26-pacitan-store-{XX.lower()}":
            found = True

    if found:
        ok("S3 Bucket")
    else:
        fail("S3 Bucket")

except:
    fail("S3 Error")


# =====================
# SQS
# =====================
try:
    qs = sqs.list_queues().get("QueueUrls", [])

    found = False

    for q in qs:
        if f"LKS26-Queue-Orders-{XX}" in q:
            found = True

    if found:
        ok("SQS Queue")
    else:
        fail("SQS Queue")

except:
    fail("SQS Error")


# =====================
# Lambda
# =====================
try:
    funcs = lam.list_functions()["Functions"]

    ingest = False
    process = False

    for f in funcs:
        if f["FunctionName"] == f"LKS26-Function-Ingest-{XX}":
            ingest = True

        if f["FunctionName"] == f"LKS26-Function-Process-{XX}":
            process = True

    if ingest:
        ok("Lambda Ingest")

    else:
        fail("Lambda Ingest")

    if process:
        ok("Lambda Process")

    else:
        fail("Lambda Process")

except:
    fail("Lambda Error")


# =====================
# ALB
# =====================
try:
    lbs = elbv2.describe_load_balancers()["LoadBalancers"]

    found = False

    for lb in lbs:
        if lb["LoadBalancerName"] == f"LKS26-ALB-{XX}":
            found = True

    if found:
        ok("ALB")

    else:
        fail("ALB")

except:
    fail("ALB Error")


# =====================
# EC2 Monitor
# =====================
try:
    inst = ec2.describe_instances()

    found = False

    for r in inst["Reservations"]:
        for i in r["Instances"]:

            if "Tags" in i:
                for t in i["Tags"]:
                    if t["Value"] == f"LKS26-Instance-Monitor-{XX}":
                        found = True

    if found:
        ok("EC2 Monitor")

    else:
        fail("EC2 Monitor")

except:
    fail("EC2 Error")


print("\n=== SELESAI ===\n")
