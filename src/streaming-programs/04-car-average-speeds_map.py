#!/usr/bin/python
import sys
import json

# Count average speeds for links

def get_locationdata(locationdata_file):
    with open(locationdata_file, "r") as jsonfile:
        return json.load(jsonfile)

def main(locationdata_file):

    locationdata = get_locationdata(locationdata_file)

    for input_line in sys.stdin:
        data = json.loads(input_line)

        for recognition in data['recognitions']:
            try:
                link_data = (item for item in locationdata['links'] if item['id'] == recognition['id']).next()
                average_speed  = (link_data['dist'] / recognition['tt']) * 3.6
                print "LongValueSum:" + str(recognition['id']) + "_speedsum\t" + str(int(average_speed))
                print "LongValueSum:" + str(recognition['id']) + "_speedcount\t1"
            except:
                pass

if __name__ == "__main__":

    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("locationdata.json")
