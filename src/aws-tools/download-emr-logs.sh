#!/bin/sh

# This script downloads EMR logs from S3 to your local computer.
# You need AWS CLI tools installed and the following in your ~/.aws/config:
#
# [profile hadoop-seminar-emr]
# region = eu-west-1
# aws_access_key_id = YOUR_IAM_KEY
# aws_secret_access_key = YOUR_IAM_SECRET

aws s3 cp s3://hadoop-seminar-emr/logs temp/emr-logs/ --recursive --profile hadoop-seminar-emr
