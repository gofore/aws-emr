#!/bin/sh

# This script uploads all the python scripts from the current directory to S3
# to be available in EMR. You need AWS CLI tools installed and the following
# profile in your ~/.aws/config:
#
# [profile hadoop-seminar-emr]
# region = eu-west-1
# aws_access_key_id = YOUR_IAM_KEY
# aws_secret_access_key = YOUR_IAM_SECRET

aws s3 cp *.py s3://hadoop-seminar-emr/digitraffic/src/ --profile hadoop-seminar-emr
