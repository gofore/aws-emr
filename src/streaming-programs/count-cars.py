#!/usr/bin/python
import sys
import json

def main():
    for input_line in sys.stdin:
        data = json.loads(input_line)
        for recognition in data['recognitions']:
            print "LongValueSum:" + str(recognition['id']) + "\t" + str(recognition['cars'])

if __name__ == "__main__":
    main()
