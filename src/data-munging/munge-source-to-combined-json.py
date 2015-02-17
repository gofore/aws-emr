#!/usr/bin/python

import sys
import os
import re
import time
import xml.etree.ElementTree as ET
import boto
import boto.s3.key
import json

'''
Takes 1-minute xml files, calculates average travel times, and concatenates the data into
a file where each line is a valid json object. New format also takes 62% of original space.

Run example:
src/data-munging/munge-source-to-combined-json.py ../imported-archives/2014/05/ hadoop-seminar-emr digitraffic/munged/links-by-date/2014/
'''

def _parse_xml_files(filenames):
    ''' Parses given xml files, calculates average travel times and returns the data as a list of json objects '''

    time_concat_start = time.time()
    concatenated_data = []

    for filename in filenames:
        xml_root = ET.parse(filename).getroot()
        parsed_data = {}
        parsed_data['date'] = xml_root.attrib.get('periodstart')
        parsed_data['recognitions'] = []

        for road_link in xml_root.iter('{http://FTT.arstraffic.com/schemas/IndividualTT/}link'):
            link_data = {}
            link_data['id'] = road_link.attrib.get('id')
            link_data['itts'] = [int(car.attrib.get('tt')) for car in road_link]
            link_data['cars'] = len(link_data['itts'])
            link_data['tt'] = sum(link_data['itts'])/link_data['cars']
            parsed_data['recognitions'].append(link_data)
        
        concatenated_data.append(json.dumps(parsed_data))

    print "{0:.2f}\tmunged {1} files".format(time.time() - time_concat_start, len(filenames))
    return concatenated_data

def _upload_data_to_s3(data, s3_output_object_key, s3_bucket, output_s3_path):
    ''' Uploads the given list of json objects as a single object to S3 '''

    time_upload_start = time.time()
    full_s3_key = output_s3_path + s3_output_object_key
    output_key = boto.s3.key.Key(s3_bucket, full_s3_key)
    output_key.set_contents_from_string('\n'.join(data))
    print "{0:.2f}\tuploaded data to s3://{1}/{2}".format(time.time() - time_upload_start, s3_bucket.name, full_s3_key)

def get_file_lists(root_input_path, batch_size):
    ''' Walks through the given yearly directory and returns a list of files '''

    batches_data = []
    pattern = re.compile("measurements-(\d\d\d\d)-(\d\d)-(\d\d)T(\d\d).(\d\d).(\d\d)Z.xml")

    batch_files = []
    last_match = ()
    for directory, subdirectories, walked_files in os.walk(root_input_path):
        subdirectories.sort()
        for walked_file in walked_files:
            source_file_match = pattern.findall(walked_file)
            if source_file_match:
                last_match = source_file_match
                batch_files.append(directory + "/" + walked_file)

    print "Number of input files", len(batch_files)
    output_s3_key = ""
    if batch_size == "month":
        output_s3_key = last_match[0][0] + "-" + last_match[0][1] + ".json"
    batch_files.sort()
    batches_data.append({'output_s3_key': output_s3_key, 'files': batch_files})
    return batches_data

def combine_and_upload(batches, output_s3_path, s3_bucket):
    #print json.dumps(batches, sort_keys=True, indent=4)
    print "Number of batches", len(batches)
    for batch in batches:
        _upload_data_to_s3(_parse_xml_files(batch['files']), batch['output_s3_key'], s3_bucket, output_s3_path)


if __name__ == "__main__":
    time_script_start = time.time()

    input_directory = sys.argv[1]
    output_s3_bucket = sys.argv[2]
    output_s3_path = sys.argv[3]
    s3_bucket = boto.connect_s3().get_bucket(output_s3_bucket)

    file_lists = get_file_lists(input_directory, "month")
    combine_and_upload(file_lists, output_s3_path, s3_bucket)

    print "{0:.2f}\ttotal run time".format(time.time() - time_script_start)
