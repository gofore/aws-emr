#!/usr/bin/python

import sys
import xml.etree.ElementTree as ET
import json

'''
One-time tool that converts the original road site list and link list from xml
to json. Because I hate xml.
'''

def tag(tag):
    return '{http://FTT.arstraffic.com/schemas/LocationData/}' + tag

def parse_xml(xml_file):

    data = {'sites':[], 'links':[]}
    xml_root = ET.parse(xml_file).getroot()
    
    for site in xml_root.iter(tag('site')):
        site_data = {}
        site_data['id'] = site.find(tag('number')).text
        site_data['rno'] = site.find(tag('RNO')).text
        site_data['tro'] = site.find(tag('TRO')).text
        site_data['lat'] = float(site.find(tag('WGS84')).attrib.get('lat'))
        site_data['lon'] = float(site.find(tag('WGS84')).attrib.get('lon'))

        for name in site.findall(tag('name')):
            if name.attrib.get('language') == 'fi':
                site_data['name'] = name.text

        data['sites'].append(site_data)

    for link in xml_root.iter(tag('link')):
        link_data = {}
        link_data['id'] = link.find(tag('linkno')).text
        link_data['dist'] = float(link.find(tag('distance')).find(tag('value')).text)
        link_data['site_start'] = link.find(tag('startsite')).text
        link_data['site_end'] = link.find(tag('endsite')).text
        
        for name in link.findall(tag('name')):
            if name.attrib.get('language') == 'fi':
                link_data['name'] = name.text

        data['links'].append(link_data)

    return data

if __name__ == "__main__":

    data = parse_xml(sys.argv[1])
    print json.dumps(data, sort_keys=True, indent=1)
