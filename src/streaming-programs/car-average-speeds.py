#!/usr/bin/python
import sys
import json

# Count average speeds for links

def main(locationdata_dictionary_file):

    locationdata = {}
    with open(locationdata_dictionary_file, "r") as dictionary_file:
        locationdata = json.load(dictionary_file)

    for input_line in sys.stdin:
        data = json.loads(input_line)

        for recognition in data['recognitions']:
            try:
                link_data = (item for item in locationdata['links'] if item['id'] == recognition['id']).next()
                average_speed  = (link_data['dist'] / recognition['tt']) * 3.6
                print "CountAverage: " + str(recognition['id']) + "\t" + str(int(average_speed))
            except:
                pass

if __name__ == "__main__":
    main(sys.argv[1])
