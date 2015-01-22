#!/usr/bin/python
import sys
import xml.etree.ElementTree as ET

# XML parsing test
# See https://hadoop.apache.org/docs/current/api/org/apache/hadoop/mapreduce/lib/aggregate/package-tree.html

def main(argv):

    root = ET.parse(sys.stdin).getroot()
    
    period_start = root.attrib.get('periodstart')
    print period_start

    for road_link in root.iter('{http://FTT.arstraffic.com/schemas/IndividualTT/}link'):
        road_link_id = road_link.attrib.get('id')
        for car in road_link:
            time = car.attrib.get('tt')
            offset = car.attrib.get('os')
            print road_link_id, time, offset


if __name__ == "__main__":
    main(sys.argv)
