import boto3
import os
import math
import time

# SQS queue
sqs_queue = boto3.client(
    "sqs",
    region_name="us-east-1",
    aws_access_key_id="null",
    aws_secret_access_key="null",
)
# web-tier ec2 instance
ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
    aws_access_key_id="null",
    aws_secret_access_key="null",
)

# set zero time
zero_instances = False
zero_time = time.time()


def run():
    global zero_instances
    global zero_time

    # Get the input queue URL
    input_queue_url = "null"

    # Get the ApproximateNumberOfMessages from the queue
    input_queue_attributes = sqs_queue.get_queue_attributes(
        QueueUrl=input_queue_url, AttributeNames=["ApproximateNumberOfMessages"]
    )
    approx_num_messages = int(
        input_queue_attributes["Attributes"]["ApproximateNumberOfMessages"]
    )

    # Get ids of the running instances
    running_ec2 = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
            {"Name": "tag:tier", "Values": ["app"]},
        ]
    )

    running_ec2_ids = []

    # List of IDs of running instances
    if running_ec2["Reservations"]:
        for res in running_ec2["Reservations"]:
            for instance in res["Instances"]:
                running_ec2_ids.append(instance["InstanceId"])
    print(approx_num_messages, running_ec2_ids)

    # Find the total number of instances required for the messages in the queue
    messages_per_instance = (
        2  # gives the number of messages to be processed by each ec2 instance
    )

    required_ec2_instances = min(
        math.ceil(approx_num_messages / messages_per_instance), 20
    )
    print("required = " + str(required_ec2_instances))

    num_current_ec2_running = len(running_ec2_ids)
    print("running = " + str(num_current_ec2_running))

    # Checking if the current required instances is zero and if there are more than zero instances running
    if required_ec2_instances == 0 and num_current_ec2_running > 0:
        # If there were zero instances required previously
        if zero_instances:
            # Calculate the minutes passed since last zero instance requirement
            mins = (time.time() - zero_time) // 60
            # If it's been less than one minute since last zero instance requirement, set the required instances to 1 to keep at least one running
            if mins < 1:
                required_ec2_instances = 1
        else:
            # If this is the first time zero instances are required, set the current time to zero_time, and set zero_instances to True to denote the first zero instances requirement
            # Set the required instances to 1 to keep at least one running
            zero_time = time.time()
            zero_instances = True
            required_ec2_instances = 1
        print("New required count: " + str(required_ec2_instances))
    # Reset zero_instances to False if now more than zero instances are required
    elif zero_instances and required_ec2_instances > 0:
        zero_instances = False

    # shell commands to run when new app-tier ec2 created
    user_data = """#!/bin/bash 
    sudo -u ubuntu -i <<'EOF'
    python3 /home/ubuntu/app-tier/index.py
    EOF"""

    # Autoscaling
    if num_current_ec2_running == required_ec2_instances:
        print("Autoscaling not required!")
    # Scaling-in
    elif num_current_ec2_running > required_ec2_instances:
        remove = num_current_ec2_running - required_ec2_instances
        print(ec2.terminate_instances(InstanceIds=running_ec2_ids[:remove]))
    # Scaling-out
    else:
        add = required_ec2_instances - num_current_ec2_running
        response = ec2.run_instances(
            ImageId="null",  # ami of the app ec2 instance 0 with all the files and libs installed
            InstanceType="t2.micro",
            KeyName="group_key_pair",
            MinCount=add,
            MaxCount=add,
            UserData=user_data,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "tier", "Value": "app"},
                        {"Key": "Name", "Value": "app-tier"},
                    ],
                },
            ],
        )
        print(response)


if __name__ == "__main__":
    while True:
        run()
        time.sleep(10)
