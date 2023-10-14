import os
import boto3
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)
res = dict()

# access key and aws details
aws_access_key_id = "null"
aws_secret_access_key = "null"
region_name = "us-east-1"

# input queue url
input_queue_url = "null"

# output queue url
output_queue_url = "null"

# sqs endpoint url
endpoint_url = "https://sqs.us-east-1.amazonaws.com"

# sqs variable
sqs = boto3.resource(
    "sqs",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    region_name=region_name,
)

# sqs client variable
sqs_client = boto3.client(
    "sqs",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    region_name=region_name,
)

# s3 variable
s3 = boto3.resource(
    service_name="s3",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


# get app home page
@app.route("/upload")
def showHomePage():
    return "Application Home Page"


# get-post for the app
@app.route("/", methods=["GET", "POST"])

# uploading images
def uploadImage():
    cnt = 0
    output = None
    print(request.files)
    if "myfile" in request.files:
        # print( request.files)
        image = request.files["myfile"]
        # image1 = request.files['myfile']
        print(image)
        im = image.read()
        f_name = str(image).split(" ")[1][1:][:-1]

        print(f_name)
        if f_name != "":
            f_extension = os.path.splitext(f_name)[1]
            print(f_extension)
            encoded_msg = base64.b64encode(im)
            value = str(encoded_msg, "ascii")
            str_byte = f_name.split(".")[0] + " " + value
            # print(str_byte)
            # print(sqs_client.send_message)
            resp = sqs_client.send_message(
                QueueUrl=input_queue_url, MessageBody=str_byte
            )

            print(resp)
            print(f_name.split(".")[0])
            try:
                output = getCorrectOutput(f_name.split(".")[0])
                print("OUTPUT")
                print(output)
                data = {
                    "text": output,
                }
                return jsonify(data)

            except Exception as e:
                print(str(e))
                return "Something went wrong!"
        else:
            return "Error with file name"
    else:
        return "File should be of type Image"

    # return jsonify("Something went wrong 2")


def getNumMsgOutputQueue():
    response = sqs.get_queue_attributes(
        QueueUrl=output_queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
        ],
    )

    return int(response["Attributes"]["ApproximateNumberOfMessages"])


def getCorrectOutput(image):
    result = ""

    while True:
        if image in res.keys():
            return res[image]

        response = sqs_client.receive_message(
            QueueUrl=output_queue_url,
            MaxNumberOfMessages=10,
            MessageAttributeNames=["All"],
        )

        if "Messages" in response:
            msgs = response["Messages"]
            for msg in msgs:
                msg_body = msg["Body"]
                # print("\n\nMSG BODY: ", msg_body)
                res_image = msg_body.split(" ")[0]
                print("RES IMG")
                print(res_image.split(".")[0])

                my_result = " ".join(msg_body.split(" ")[1:])

                print("\n\nmy_result: ", my_result)
                res[res_image] = my_result

                # res[res_image] = msg_body.split(" ")[1]

                receipt_handle = msg["ReceiptHandle"]
                # print(receipt_handle)
                # print(msg_body.split(" ")[1])
                sqs_client.delete_message(
                    QueueUrl=output_queue_url, ReceiptHandle=receipt_handle
                )

                # print("??")
                print(res_image.split(".")[0])
                print(image)
                if res_image.split(".")[0] == image:
                    return res[res_image]


if __name__ == "__main__":
    # print("hello")
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8081)))