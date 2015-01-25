
# Amazon Elastic MapReduce

Ville Seppänen [@Vilsepi](https://twitter.com/Vilsepi) | Jari Voutilainen [@Zharktas](https://twitter.com/Zharktas) | [@GoforeOy](https://twitter.com/GoforeOy)

---

## Agenda

1. Introduction to Elastic MapReduce
2. Simple EMR demo
3. Introduction to our dataset
4. Examples and findings

All presentation material is available at [https://github.com/gofore/aws-emr](https://github.com/gofore/aws-emr)

---

# Elastic MapReduce (EMR)

--

## [Amazon Elastic MapReduce](http://aws.amazon.com/elasticmapreduce/)

- MapReduce cluster as a service
- Hadoop-based

---

# Quick EMR demo

--

![Say 'word count' one more time](/images/word_count_meme.jpg)

[The endlessly fascinating example of counting words in Hadoop](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-get-started-count-words.html)

--

- Cluster Configuration: name, logging
- Tags: keywords for the cluster
- Software Configuration: Hadoop version, Hive, Pig, HBase, Ganglia...
- File System Configuration: EMRFS file encryption, consistency
- Hardware Configuration: master, code and task nodes
- Security and Access: ssh keys, node access roles
- Bootstrap Actions: scripts to initialize the cluster
- Steps: a queue of jobs of the cluster

--

## [WordSplitter.py](https://s3.amazonaws.com/elasticmapreduce/samples/wordcount/wordSplitter.py)

<pre><code data-trim="" class="java">
#!/usr/bin/python
import sys
import re

def main(argv):
    pattern = re.compile("[a-zA-Z][a-zA-Z0-9]*")
    for line in sys.stdin:
        for word in pattern.findall(line):
            print "LongValueSum:" + word.lower() + "\t" + "1"

if __name__ == "__main__":
    main(sys.argv)
</code></pre>

--

## Filesystems

- EMRFS and Hadoop
- S3 and S3n
- S3 is not a file system

http://wiki.apache.org/hadoop/AmazonS3

---

# Our dataset

--

[Digitraffic](http://www.infotripla.fi/digitraffic/doku.php?id=start_en) is a service offering real time information and data about the traffic, weather and condition information on the Finnish main roads.

The service is provided by the [Finnish Transport Agency](http://www.liikennevirasto.fi), and produced by [Gofore](http://gofore.com) and [Infotripla](http://infotripla.fi).

--

## Traffic fluency

- Our data consists of traffic fluency information, i.e. how quickly vehicles have been identified to pass through a road segment (*a link*).
- Data is gathered with camera-based [Automatic License Plate Recognition (ALPR)](http://en.wikipedia.org/wiki/Automatic_number_plate_recognition), and more recently with mobile-device-based [Floating Car Data (FCD)](http://en.wikipedia.org/wiki/Floating_car_data).

--

![Road segments](/images/road_segments_map.png)

[Travel time link network](http://www.infotripla.fi/digitraffic/lib/exe/fetch.php?media=linkkiverkosto.pdf)

--

```
<link>
  <linkno>310102</linkno>
  <startsite>1108</startsite>
  <endsite>1107</endsite>
  <name language="en">Hallila -> Kaukajärvi</name>
  <name language="fi">Hallila -> Kaukajärvi</name>
  <name language="sv">Hallila -> Kaukajärvi</name>
  <distance>
    <value>3875.000</value>
    <unit>m</unit>
  </distance>
</link>
```

[Static link information](http://www.infotripla.fi/digitraffic/lib/exe/fetch.php?tok=a8263d&media=http%3A%2F%2Fwww.infotripla.fi%2Fdigitraffic%2Fdocs%2FLocationData.XML)

Links are one-way

--

```
<ivjtdata duration="60" periodstart="2014-06-24T02:55:00Z">
  <recognitions>
    <link id="110302" data_source="1">
      <recognition offset_seconds="8" travel_time="152"></recognition>
      <recognition offset_seconds="36" travel_time="155"></recognition>
    </link>
    <link id="410102" data_source="1">
      <recognition offset_seconds="6" travel_time="126"></recognition>
      <recognition offset_seconds="45" travel_time="152"></recognition>
    </link>
    <link id="810502" data_source="1">
      <recognition offset_seconds="25" travel_time="66"></recognition>
      <recognition offset_seconds="34" travel_time="79"></recognition>
      <recognition offset_seconds="35" travel_time="67"></recognition>
      <recognition offset_seconds="53" travel_time="58"></recognition>
    </link>
  </recognitions>
</ivjtdata>
```

Each file contains finished passthroughs for each road segment during one minute.

--

## Some numbers

- x Links (road segments)
- 525600 XML files per year
- x file size compressed/uncompressed
- x timespan
- x number of observations/recognitions

---

# Prerequisites

--

## Uploading the data to Amazon S3

Data was given as monthly tar.gz archive files. We unpack the data and use AWS CLI tools to upload the XML files to S3.

--

## The small files problem

- We have approximately 4 million files.
- "Small files are a big problem in Hadoop" [1](http://blog.cloudera.com/blog/2009/02/the-small-files-problem/)[2](http://amilaparanawithana.blogspot.fi/2012/06/small-file-problem-in-hadoop.html)[3](http://www.idryman.org/blog/2013/09/22/process-small-files-on-hadoop-using-combinefileinputformat-1/)
- Concatenate data into bigger chunks


--

## Parsing XML with Hadoop Streaming

- [Hadoop Tutorial 2.1 -- Streaming XML Files](http://cs.smith.edu/dftwiki/index.php/Hadoop_Tutorial_2.1_--_Streaming_XML_Files)
- Hadoop Streaming docs: [How do I parse XML documents using streaming?](http://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/HadoopStreaming.html#How_do_I_parse_XML_documents_using_streaming)
- [Processing XML With Hadoop Streaming](http://davidvhill.com/article/processing-xml-with-hadoop-streaming)

---

# Summary

--

[AWS EMR Best practices](https://media.amazonwebservices.com/AWS_Amazon_EMR_Best_Practices.pdf)
