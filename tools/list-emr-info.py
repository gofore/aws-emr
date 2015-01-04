#!/usr/bin/env python

# This script connects to AWS and prints out information of
# EMR clusters. You need IAM credentials exported as env variables.
# See the export_env_variables.sh

import boto
import boto.emr
import pprint

conn = boto.emr.connect_to_region('eu-west-1')

for cluster in conn.list_clusters().clusters:
	pprint.pprint(vars(cluster))
	pprint.pprint(vars(cluster.status))
