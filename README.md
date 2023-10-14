# Cloud 9 - CSE 546 Project 1

## Team Members

- Awani Kendurkar 1225438149
- Shivani Nandani 1225446014
- Sidharth Dinesh 1225238352

## Individual Tasks

### Awani Kendurkar 1225438149

1. Created a POST API for the users to send HTTP requests to and designed a simple Flask server.
2. Performed encoding of the images to be sent to the SQS queue.
3. Wrote the logic to facilitate sending messages to the SQS request queue and also listening for the output through the SQS response queue.
4. Conducted testing and ensured code standards.
5. Worked on the report and documentation.

### Shivani Nandani 1225446014

1. Wrote functional code to decode in the input images from the request queue and run the image classification model on them.
2. Created the logical flow to upload input images to an S3 bucket and image classification output to another S3 bucket.
3. Also wrote the code to send output messages to the SQS response queue.
4. Conducted testing and ensured code standards.
5. Worked on the report and documentation.

### Sidharth Dinesh 1225238352

1. Implemented the logic to handle scaling in and scaling out of the EC2 instances.
2. Wrote a shell script for automating the newly created instances.
3. Created the web-tier and app-tier EC2 instances, the input and output SQS queues, and the input and output S3 buckets on AWS console.
4. Conducted testing and ensured code standards.
5. Worked on the report and documentation.

## More Details

### AWS Credentials

```bash
ACCESS_KEY_ID="null"
SECRET_ACCESS_KEY="null"
```

### PEM Key

See file `null`.

### Web-Tier URL

The web-tier URL is `null`.

### SQS Queue Names and URLs

```bash
SQS_REQUEST_QUEUE_NAME="null"
SQS_REQUEST_QUEUE_URL="null"
```

```bash
SQS_RESPONSE_QUEUE_NAME="null"
SQS_RESPONSE_QUEUE_URL="null"
```

### S3 Bucket Names

```bash
S3_INPUT_BUCKET="null"
S3_OUTPUT_BUCKET="null"
```
