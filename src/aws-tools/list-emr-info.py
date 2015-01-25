#!/usr/bin/env python

# This script connects to AWS and prints out information of EMR clusters.
# You need IAM credentials exported as env variables (See export_env_variables.sh).

import boto
import boto.emr
import pprint

conn = boto.emr.connect_to_region('eu-west-1')

def get_clusters():
    for cluster in conn.list_clusters().clusters:
        
        cluster_info = cluster.__dict__
        cluster_info['status'] = cluster.status.__dict__
        cluster_info['status']['timeline'] = cluster.status['timeline'].__dict__
        
        instance_groups_infos = conn.list_instance_groups(cluster.id).instancegroups
        instances = []
        for instance_group in instance_groups_infos:
            instances.append(instance_group.__dict__)

        cluster_info['instances'] = instances
        
        pprint.pprint(cluster_info, indent=4)
        print "\n"

def get_jobflows():
    for jobflow in conn.describe_jobflows():
        pprint.pprint(vars(jobflow))
        try:
            if jobflow.instancegroups:
                for instancegroup in jobflow.instancegroups:
                    pprint.pprint(vars(instancegroup), indent=8)
        except:
            pass
        print "\n"

if __name__ == "__main__":
    get_clusters()
