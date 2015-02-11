#!/usr/bin/python
import sys
import re
import json
import operator
from collections import defaultdict
from collections import OrderedDict

# Sorts and prints a human-readable list of average speeds on links

def get_locationdata(locationdata_file):
    with open(locationdata_file, "r") as jsonfile:
        return json.load(jsonfile)

def main(output_file, locationdata_file):

    locationdata = get_locationdata(locationdata_file)

    results = defaultdict(dict)
    with open(output_file, "r") as resultlines:

        pattern = re.compile("(\d*)_speed(.*)\t(\d*)")
        for resultline in resultlines:
            match = pattern.findall(resultline)
            if match:
                link_id = match[0][0]
                data_type = match[0][1]
                data_value = int(match[0][2])
                results[link_id][data_type] = data_value

    for link_id, link in results.iteritems():
        link['speed'] = link['sum']/link['count']
        link['name'] = (item for item in locationdata['links'] if item['id'] == link_id).next()['name']

    sorted_results = OrderedDict(sorted(results.items(), key=lambda x :x[1]['speed'], reverse=True))
    for link_id, link in sorted_results.iteritems():
        print str(link['speed']) + "\t" + link['name']

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
