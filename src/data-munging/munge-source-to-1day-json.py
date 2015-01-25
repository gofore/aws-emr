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
Takes all 1-minute xml files of a day, calculates average travel times, and
concatenates the data into 1-day json files. New format also takes
62% of original space.

Run example:
./munge-source-to-1day-json.py \
  /tmp/source-data/2014/06/ \
  hadoop-seminar-emr \
  digitraffic/munged/links-by-date/2014/

'''

def _parse_xml_files(filenames, directory):
    ''' Parses given xml files from the given directory, calculates average 
        travel times and returns the data as a list of json objects '''

    time_concat_start = time.time()
    concatenated_data = []

    for filename in filenames:
        xml_root = ET.parse(directory + "/" + filename).getroot()
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

    print "{0:.2f}\tmunged {1} files from {2}".format(time.time() - time_concat_start, len(filenames), directory)
    return concatenated_data

def _upload_data_to_s3(data, s3_output_object_key, s3_bucket):
    ''' Uploads the given list of json data as a single object to S3 '''

    time_upload_start = time.time()
    output_key = boto.s3.key.Key(s3_bucket, s3_output_object_key)
    output_key.set_contents_from_string('\n'.join(data))
    print "{0:.2f}\tuploaded data to s3://{1}/{2}".format(time.time() - time_upload_start, s3_bucket.name, s3_output_object_key)

def combine_and_upload(root_input_path, output_path, s3_bucket):
    ''' Walks through the given yearly directory, converts and uploads each 
        1-minute xml files as 1-day json files '''

    path_pattern = re.compile("(\d\d\d\d)/(\d\d)/(\d\d)")
    for directory, subdirectories, files in os.walk(root_input_path):
        matches = path_pattern.findall(directory)
        if matches:
            date = "-".join(matches[0])
            # TODO: We should probably sort 'files' here, otherwise data ends up in random order
            _upload_data_to_s3(_parse_xml_files(files, directory), output_path+date+".json", s3_bucket)

if __name__ == "__main__":
    time_script_start = time.time()
    
    input_directory = sys.argv[1]
    output_s3_bucket = sys.argv[2]
    output_s3_path = sys.argv[3]

    s3_bucket = boto.connect_s3().get_bucket(output_s3_bucket)
    combine_and_upload(input_directory, output_s3_path, s3_bucket)

    print "{0:.2f}\ttotal run time".format(time.time() - time_script_start)
