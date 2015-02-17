
## Directory contents

- **aws-tools:** Scripts to manage AWS resources instead of doing them manually from the web UI.
- **data-munging:** Manual tools (mainly in EC2 and uploading to S3) to pre-munge the data before EMR. If the munging is complicated, it should obviously be done with EMR.
- **example-data:** Small snippets of input test data for local development.
- **result-analysis:** Manual tools for visualizing the result data.
- **streaming-programs:** Python scripts that are fully compatible to be run as Hadoop Streaming programs (as mappers, reducers etc).
- **sync-to-s3.sh:** A script that synchronizes all files under current directory to S3 (except for files under `temp/` where you can put your local-only files). Run this to make your streaming program available to EMR.

## Prerequisites

Create AWS root account, create IAM user account, give necessary permissions (S3, EC2, EMR) to the user and generate API credentials. Place the `credentials.csv` to the project root directory.

Most of the scripts require boto and/or awscli which you need to install:

    sudo apt-get install python-pip
    sudo pip install boto awscli

The scripts that use AWS CLI tools expect that the following profile exists in ~/.aws/config:

    [profile hadoop-seminar-emr]
    region = eu-west-1
    aws_access_key_id = YOUR_IAM_KEY
    aws_secret_access_key = YOUR_IAM_SECRET

Boto expects that the credentials are exported as env variables. Place your `credentials.csv` in the project root (see script file for further instructions) and run:

    . aws-tools/export_env_variables.sh

Once you have boto and awscli installed and the env variables installed, you can run the scripts:

    aws-tools/list-emr-info.py

## Local development

Develop Hadoop streaming programs locally by passing the example input data to it in stdin:

    cat example-data/input-data-example.xml | python streaming-programs/01-wordsplit_map.py
    cat example-data/2014-06-01-subset.json | python streaming-programs/04-car-average-speeds_map.py example-data/locationdata.json
    cat example-data/2014-06-01-subset.json | python streaming-programs/05-car-speed-for-time-of-day_map.py example-data/locationdata.json

Once the output looks good, upload the streaming program to S3 with the upload script, and run it in EMR.

## Using EMR

    # Export credentials
    . aws-tools/export_env_variables.sh
    
    # Start a cluster
    aws-tools/run-jobs.py create-cluster "Car speed counting cluster"
    aws-tools/run-jobs.py run-step j-2B7Y5H23AFWHX 05-car-speed-for-time-of-day_map.py digitraffic/munged/links-by-date/2014
    
    # Download and concatenate results
    aws s3 cp s3://hadoop-seminar-emr/digitraffic/outputs/2015-02-16_20-46-33_05-car-speed-for-time-of-day_map.py/ /tmp/emr --recursive --profile hadoop-seminar-emr
    cat /tmp/emr/part-* > /tmp/emr/output
    
    # Visualize results
    result-analysis/05-car-speed-for-time-of-day_output.py /tmp/emr/output example-data/locationdata.json
