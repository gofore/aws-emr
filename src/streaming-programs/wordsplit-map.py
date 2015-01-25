#!/usr/bin/python
import sys
import re

# Test application to check whether EMR pipeline and reading the data works
# This code is from the EMR example:
# https://s3.amazonaws.com/elasticmapreduce/samples/wordcount/wordSplitter.py

def main(argv):
    pattern = re.compile("[a-zA-Z][a-zA-Z0-9]*")
    for line in sys.stdin:
        for word in pattern.findall(line):
            print "LongValueSum:" + word.lower() + "\t" + "1"

if __name__ == "__main__":
    main(sys.argv)
