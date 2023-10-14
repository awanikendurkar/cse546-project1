import base64
from urllib import response
import boto3
from botocore.exceptions import ClientError
import os
import time
import datetime
import logging
import io

# access key information
aws_access_key_id = "null"
aws_secret_access_key = "null"
region_name = "us-east-1"

# input queue url
input_queue_url = "null"

# output queue url
output_queue_url = "null"

# sqs endpoint url
endpoint_url = "https://sqs.us-east-1.amazonaws.com"

# s3 buckets to store input images and output classification
s3_input_bucket = "null"
s3_output_bucket = "null"

# initializations
sqs = boto3.client(
    "sqs",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    region_name=region_name,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

s3 = boto3.resource(
    service_name="s3",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


# function to receive messages
def receiveMessages():
    print("Receiving messages...")
    try:
        response = sqs.receive_message(
            QueueUrl=input_queue_url,
            AttributeNames=["SentTimestamp"],
            MaxNumberOfMessages=10,
            MessageAttributeNames=["All"],
            VisibilityTimeout=30,
            WaitTimeSeconds=10,
        )

        # print("resp")
        # print(response)

    except Exception as e:
        print(str(e))
        return "Something went wrong"

    if "Messages" in response:
        receipt_handle = response["Messages"][0]["ReceiptHandle"]
        rr = response["Messages"]

        print("rr")
        print(rr)
        deleteMessage(receipt_handle)
        return rr
    else:
        time.sleep(1)
        return receiveMessages()


# function to delete messages if not correct
def deleteMessage(receipt_handle):
    sqs.delete_message(QueueUrl=input_queue_url, ReceiptHandle=receipt_handle)


# decode message to get data
def decodeMessage(file_name, msg):
    decoded_msg = open(file_name, "wb")
    decoded_msg.write(base64.b64decode((msg)))
    decoded_msg.close()


# send message to output queue
def sendMessageToOutputQueue(file_name, msg):
    resp = sqs.send_message(
        QueueUrl=output_queue_url, MessageBody=(file_name + " " + msg)
    )


# function to upload images to input bucket
def uploadToS3InputBucket(file_name, bucket, object_name):
    try:
        response = s3_client.upload_fileobj(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# function to upload classification output to output bucket
def uploadToS3OutputBucket(s3, bucket_name, image_name, predicted_result):
    content = (image_name, predicted_result)
    content = " ".join(str(x) for x in content)
    s3.Object(s3_output_bucket, image_name).put(Body=content)


# start and wait for messages
def initialize():
    val = receiveMessages()

    if val == None or len(val) == 0:
        # print("here in none condition")
        return

    message = val[0]
    print(message)

    file_name, encoded_msg = message["Body"].split()
    img_file_name = file_name
    file_name = file_name + ".jpeg"
    logging.info("file name : " + file_name)

    # print("message body")
    # print(message["Body"])

    print("File name: ", end="\t\t")
    print(file_name)

    msg_value = bytes(encoded_msg, "ascii")
    qp = base64.b64decode(msg_value)
    print(qp)
    with open(file_name, "wb") as fff:
        fff.write(qp)

    with open(file_name, "rb") as f:
        if uploadToS3InputBucket(f, s3_input_bucket, file_name):
            logging.info("input file uploaded in S3 bucket")
            print("Input file uploaded in S3 bucket.")

    stdout = os.popen(f' python3 ./image_classification.py "{file_name}"')
    result = stdout.read().strip()
    logging.info("result : " + result)
    print("result " + result)

    uploadToS3OutputBucket(s3, s3_output_bucket, img_file_name, result)
    sendMessageToOutputQueue(img_file_name, result)
    if os.path.exists(file_name):
        os.remove(file_name)
    print(result)


logging.info("Timestamp : " + str(datetime.datetime.now()))
while True:
    initialize()