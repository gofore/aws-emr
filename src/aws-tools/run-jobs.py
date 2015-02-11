#!/usr/bin/env python

# This script creates an EMR cluster and runs jobs on it
# You need IAM credentials exported as env variables (See export_env_variables.sh).

import sys
import datetime
import boto.emr
from boto.emr.instance_group import InstanceGroup


def create_new_steps(streaming_program, input_data_path, s3_bucket):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = "s3://{0}/digitraffic/outputs/{1}/".format(s3_bucket, timestamp + "_" + streaming_program)

    steps = []
    steps.append(boto.emr.step.StreamingStep(
        "Streaming app " + streaming_program,
        input="s3://{0}/{1}".format(s3_bucket, input_data_path),
        output=output_path,
        mapper=streaming_program,
        reducer="aggregate",
        combiner=None,
        cache_files=[
            "s3://{0}/digitraffic/src/streaming-programs/{1}#{1}".format(s3_bucket, streaming_program),
            "s3://{0}/digitraffic/{1}#{1}".format(s3_bucket, "locationdata.json")
            ],
        cache_archives=None,
        step_args=None,
        action_on_failure='CANCEL_AND_WAIT',
        jar='/home/hadoop/contrib/streaming/hadoop-streaming.jar'))
    print "Step will output data to", output_path
    return steps

def create_new_cluster(conn, s3_bucket, cluster_name, keep_alive=True, worker_type="m1.small", worker_count=2):

    # Note: for testing purposes, you can run ami_version 2.4.9 on m1.small instances.
    # For newer Hadoop, use 3.3.1 and m1.medium or m3.xlarge
    # on-demand prices for m1.small and m1.medium are 0.047 and 0.095 respectively
    master_node = "m1.medium"
    ami_version = "3.3.1"
    bid_price = "0.012"
    if worker_type == "m1.small":
        master_node = "m1.small"
        ami_version = "2.4.9"
        bid_price = "0.012"

    instance_groups = []
    instance_groups.append(InstanceGroup(
        name="Main node",
        role="MASTER",
        num_instances=1,
        type=master_node,
        market="ON_DEMAND"))
    instance_groups.append(InstanceGroup(
        name="Worker nodes",
        role="CORE",
        num_instances=worker_count,
        type=worker_type,
        market="ON_DEMAND"))
    instance_groups.append(InstanceGroup(
        name="Optional spot-price nodes",
        role="TASK",
        num_instances=worker_count,
        type=worker_type,
        market="SPOT",
        bidprice=bid_price))

    jobflow_id = conn.run_jobflow(
        cluster_name,
        instance_groups=instance_groups,
        action_on_failure='CANCEL_AND_WAIT',
        keep_alive=keep_alive,
        enable_debugging=True,
        log_uri="s3://{0}/logs/".format(s3_bucket),
        ami_version="2.4.9",
        bootstrap_actions=[],
        additional_info=None,
        ec2_keyname="hadoop-seminar-emr",
        visible_to_all_users=True,
        job_flow_role="EMR_EC2_DefaultRole",
        service_role="EMR_DefaultRole")

    print "Starting cluster", jobflow_id, cluster_name
    if keep_alive:
        print "Note: cluster will be left running, remember to terminate it manually after you are done!"

def run_steps_on_existing_cluster(conn, steps, cluster_id):
    conn.add_jobflow_steps(cluster_id, steps)


if __name__ == "__main__":

    usage = """Usage:
            Create new cluster without jobs:
            ./run-jobs.py create-cluster "Car counting cluster"
            Add a job to an existing cluster:
            ./run-jobs.py run-step j-2SMBD40W50QQD count-cars.py digitraffic/munged/links-by-date/2014
            """
    if len(sys.argv) < 3:
        print usage
        sys.exit()

    connection = boto.emr.connect_to_region('eu-west-1')

    if sys.argv[1] == "create-cluster":
        cluster_params = {
            "cluster_name": sys.argv[2],
            "worker_type": "m1.small",
            "worker_count": 2,
            "keep_alive": True,
            "s3_bucket": "hadoop-seminar-emr"
        }
        create_new_cluster(connection, **cluster_params)

    elif sys.argv[1] == "run-step":
        step_params = {
            "streaming_program": sys.argv[3],
            "input_data_path": sys.argv[4],
            "s3_bucket": "hadoop-seminar-emr"
        }
        steps = create_new_steps(**step_params)

        cluster_id = sys.argv[2]
        run_steps_on_existing_cluster(connection, steps, cluster_id)
    else:
        print "Unknown command"
        print usage
