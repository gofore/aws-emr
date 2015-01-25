#!/bin/bash

# This script syncs the contents of the current local directory to S3 to be
# available in EMR. A directory named 'temp' will be ignored if you have one.
# You need AWS CLI tools installed and the following profile in your
# ~/.aws/config:
#
# [profile hadoop-seminar-emr]
# region = eu-west-1
# aws_access_key_id = YOUR_IAM_KEY
# aws_secret_access_key = YOUR_IAM_SECRET

S3_TARGET_DIR="s3://hadoop-seminar-emr/digitraffic/src/"

read -r -p "Warning: Sync contents of current directory to '$S3_TARGET_DIR'? [y/N] " response
response=${response,,} # to lower-case
if [[ $response =~ ^(yes|y)$ ]]; then

  aws s3 sync . $S3_TARGET_DIR --exclude "temp/*" --profile hadoop-seminar-emr

else
  echo "Aborting."
fi
