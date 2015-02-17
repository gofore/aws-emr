#!/usr/bin/python
import sys
import re
import json
import operator
from collections import defaultdict
from collections import OrderedDict
from flask import Flask, jsonify
import random

app = Flask(__name__)
output_file = sys.argv[1]
locationdata_file = sys.argv[2]

drawable_series = []
number_of_items_to_return = 10
ignore_list = [112, 184]

# Sorts and prints a human-readable list of average speeds on links for each hour of day

def get_locationdata():
    with open(locationdata_file, "r") as jsonfile:
        return json.load(jsonfile)

def get_drawable_series():

    locationdata = get_locationdata()
    lowest_link_id  = 0
    highest_link_id = 99999999

    results = defaultdict(lambda : defaultdict(dict))
    with open(output_file, "r") as resultlines:

        pattern = re.compile("(\d*)_(\d*)_speed(.*)\t(\d*)")
        for resultline in resultlines:
            match = pattern.findall(resultline)
            if match:
                link_id = match[0][0]
                hour_of_day = match[0][1]
                data_type = match[0][2]
                data_value = int(match[0][3])

                if int(link_id) not in ignore_list:
                    if int(link_id) >= lowest_link_id and int(link_id) <= highest_link_id:
                        results[link_id][hour_of_day][data_type] = data_value
    
    for link_id, link_hour_stats in results.iteritems():
        name = (item for item in locationdata['links'] if item['id'] == link_id).next()['name']
        link_series = {'name': u"{0} ({1})".format(name, str(link_id)), 'data':[], 'link_id': link_id}

        for hour, link_hour in link_hour_stats.iteritems():
            speed = link_hour['sum'] / link_hour['count']
            link_series['data'].append({'x': int(hour)*3600, 'y': speed})

        drawable_series.append(link_series)

    for sortable in drawable_series:
        sortable['data'].sort()

    #print json.dumps(drawable_series, indent=2)
    #print len(drawable_series['series'])

def get_random_subset(size):
    return random.sample(drawable_series, size)

@app.route("/")
def root():
    return app.send_static_file('index.html')

@app.route("/data")
def data():
    return jsonify(series=get_random_subset(number_of_items_to_return))

if __name__ == "__main__":
    get_drawable_series()
    app.run(host='0.0.0.0', port=9000, debug=True)
