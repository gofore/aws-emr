#!/usr/bin/env python

# This script creates an EMR cluster and runs wordcounter.
# You need IAM credentials exported as env variables (See export_env_variables.sh).

import boto.emr
import datetime
from boto.emr.instance_group import InstanceGroup

conn = boto.emr.connect_to_region('eu-west-1')

s3_bucket = "hadoop-seminar-emr"
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
cluster_name = timestamp + " Boto wordcounter"

steps = []
steps.append(boto.emr.step.StreamingStep(
    "Wordcount app",
    input="s3://{0}/digitraffic/imported/subset-1hour".format(s3_bucket),
    output="s3://{0}/digitraffic/outputs/{1}/".format(s3_bucket, timestamp),
    mapper="test-wordsplitter.py",
    reducer="aggregate",
    combiner=None,
    cache_files=["s3://{0}/digitraffic/src/test-wordsplitter.py#test-wordsplitter.py".format(s3_bucket)],
    cache_archives=None,
    step_args=None,
    action_on_failure='TERMINATE_JOB_FLOW',
    jar='/home/hadoop/contrib/streaming/hadoop-streaming.jar'))

# Note: for testing purposes, you can run ami_version 2.4.9 on m1.small instances.
# For newer Hadoop, use 3.3.1 and m1.medium or m3.xlarge
instance_groups = []
instance_groups.append(InstanceGroup(
    name="Main node",
    role="MASTER",
    num_instances=1,
    type="m1.small",
    market="ON_DEMAND"))
instance_groups.append(InstanceGroup(
    name="Worker nodes",
    role="CORE",
    num_instances=2,
    type="m1.small",
    market="ON_DEMAND"))
instance_groups.append(InstanceGroup(
    name="Optional spot-price nodes",
    role="TASK",
    num_instances=2,
    type="m1.small",
    market="SPOT",
    bidprice="0.01"))

jobflow_id = conn.run_jobflow(
    cluster_name,
    instance_groups=instance_groups,
    action_on_failure='TERMINATE_JOB_FLOW',
    keep_alive=False,
    enable_debugging=True,
    log_uri="s3://{0}/logs/".format(s3_bucket),
    ami_version="2.4.9",
    steps=steps,
    bootstrap_actions=[],
    additional_info=None,
    ec2_keyname="hadoop-seminar-emr",
    visible_to_all_users=True,
    job_flow_role="EMR_EC2_DefaultRole",
    service_role="EMR_DefaultRole")

print "Starting cluster", jobflow_id
