#!/usr/bin/python
import sys
import boto

s3_bucket = boto.connect_s3().get_bucket('hadoop-seminar-emr')

def print_s3_key_hierarchy(depth_left, key_prefix):
    for key in s3_bucket.list(prefix=key_prefix, delimiter='/'):
        if isinstance(key, boto.s3.key.Key):
            print " ({0})".format(key.name)
        else:
            print key.name
            if depth_left > 0:
                print_s3_key_hierarchy(depth_left-1, key.name)

root = '' if len(sys.argv) < 2 else sys.argv[1]
print_s3_key_hierarchy(2, root)
