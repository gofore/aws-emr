#!/usr/bin/python
import sys
import xml.etree.ElementTree as ET

# XML parsing test
# See https://hadoop.apache.org/docs/current/api/org/apache/hadoop/mapreduce/lib/aggregate/package-tree.html

def main(argv):

    root = ET.parse(sys.stdin).getroot()
    period_start = root.attrib.get('periodstart')

    for road_link in root.iter('{http://FTT.arstraffic.com/schemas/IndividualTT/}link'):
        road_link_id = road_link.attrib.get('id')
        road_link_times = [int(car.attrib.get('tt')) for car in road_link]

        number_of_cars = len(road_link_times)
        average_travel_time = sum(road_link_times)/number_of_cars
        print "{0}\t{1} {2}".format(road_link_id, average_travel_time, number_of_cars)


if __name__ == "__main__":
    main(sys.argv)
