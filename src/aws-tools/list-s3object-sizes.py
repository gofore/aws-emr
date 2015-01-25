#!/usr/bin/python
import boto

conn = boto.connect_s3()
s3_bucket = conn.get_bucket('hadoop-seminar-emr')

total_size = 0
for key in s3_bucket.list('digitraffic/imported/2014/06/01/'):
    total_size += key.size

print total_size/1024/1024

