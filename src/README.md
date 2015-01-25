
## Directory contents

- **Data-munging:** Contains manual tools (mainly in EC2 and uploading to S3) to pre-munge the data before EMR. If the munging is complicated, it should obviously be done with EMR.
- **Example-data:** Contains small snippets of input test data for local development.
- **Streaming-programs:** Contains only Python scripts that are fully compatible to be run as Hadoop Streaming programs (as mappers, reducers etc).
- **sync-to-s3.sh:** A script that synchronizes ALL files under `src/` to S3. Run this to make your streaming program available to EMR.

## Prerequisites

Create AWS root account, create IAM user account, give necessary permissions (S3, EC2, EMR) to the user and generate API credentials. Place the credentials.csv to the project root directory.

Most of the scripts require boto and/or awscli which you need to install:

    sudo apt-get install python-pip
    sudo pip install boto awscli

The scripts that use AWS CLI tools expect that the following profile exists in ~/.aws/config:

    [profile hadoop-seminar-emr]
    region = eu-west-1
    aws_access_key_id = YOUR_IAM_KEY
    aws_secret_access_key = YOUR_IAM_SECRET

Boto expects that the credentials are exported as env variables (see file for further instructions):

    . tools/export_env_variables.sh

Once we have boto and awscli installed and the env variables installed, we can run the scripts:

    tools/list-emr-info.py

## Local development

Develop Hadoop streaming programs locally by passing the example input data to it in stdin:

    cat example-data/source-data-example.xml | python streaming-programs/wordsplit-map.py

Once the output looks good, upload the streaming program to S3 with the upload script, and run it in EMR.
