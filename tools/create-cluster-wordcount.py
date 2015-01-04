#!/usr/bin/env python

# This script creates an EMR cluster and runs wordcounter.
# You need IAM credentials exported as env variables (See export_env_variables.sh).

import boto
import boto.emr
import datetime

conn = boto.emr.connect_to_region('eu-west-1')

s3_bucket = "hadoop-seminar-emr"
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

cluster_name = timestamp + " Boto wordcounter"
steps = []

steps.append(boto.emr.step.StreamingStep(
    "Wordcount app",
    mapper="s3://{0}/digitraffic/src/test-wordsplitter.py".format(s3_bucket),
    reducer="aggregate",
    combiner=None,
    input="s3://{0}/digitraffic/imported/subset-1hour".format(s3_bucket),
    output="s3://{0}/digitraffic/outputs/{1}/".format(s3_bucket, timestamp),
    action_on_failure='TERMINATE_JOB_FLOW',
    cache_files=None,
    cache_archives=None,
    step_args=None,
    jar='/home/hadoop/contrib/streaming/hadoop-streaming.jar'))

jobflow_id = conn.run_jobflow(
    cluster_name,
    master_instance_type='m1.medium',
    slave_instance_type='m1.medium',
    num_instances=2,
    action_on_failure='TERMINATE_JOB_FLOW',
    keep_alive=True,
    enable_debugging=True,
    log_uri="s3://{0}/logs/".format(s3_bucket),
    hadoop_version="2.4.0",
    ami_version="3.3.1",
    steps=steps,
    bootstrap_actions=[],
    availability_zone=None,
    instance_groups=None,
    additional_info=None,
    api_params=None,
    ec2_keyname="hadoop-seminar-emr",
    visible_to_all_users=True,
    job_flow_role="EMR_EC2_DefaultRole",
    service_role="EMR_DefaultRole")

print "Starting cluster", jobflow_id
