#!/usr/bin/python
import sys
import json

for input_line in sys.stdin:
    data = json.loads(input_line)
    for recognition in data['recognitions']:
        print "LongValueSum:" + str(recognition['id']) + "\t" + str(recognition['cars'])
