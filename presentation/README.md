
# Amazon Elastic MapReduce

Ville Seppänen [@Vilsepi](https://twitter.com/Vilsepi) | Jari Voutilainen [@Zharktas](https://twitter.com/Zharktas) | [@GoforeOy](https://twitter.com/GoforeOy)

---

## Agenda

1. Introduction to Hadoop Streaming and Elastic MapReduce
2. Simple EMR web interface demo
3. Introduction to our dataset
4. Using EMR from command line with boto

All presentation material is available at [https://github.com/gofore/aws-emr](https://github.com/gofore/aws-emr)

---

## Hadoop Streaming

- Utility that allows you to create and run Map/Reduce jobs with any executable or script as the mapper and/or the reducer.

<pre><code data-trim="" class="shell">
$HADOOP_HOME/bin/hadoop jar $HADOOP_HOME/hadoop-streaming.jar \
    -input   my/Input/Directories \
    -output  my/Output/Directory  \
    -mapper  myMapperProgram.py   \
    -reducer myReducerProgram.py
</code></pre>

<pre><code data-trim="" class="shell">
cat input_data.txt | mapper.py | reducer.py > output_data.txt
</code></pre>

---

# Elastic MapReduce (EMR)

--

## [Amazon Elastic MapReduce](http://aws.amazon.com/elasticmapreduce/)

- Hadoop-based MapReduce cluster as a service
- In goes data and streaming programs, out comes more data
- All this can be configured from web UI or through API

--

## Hadoop streaming in EMR

![EMR and S3](/images/streaming-in-emr.png)

---

# Quick EMR demo

--

![Say 'word count' one more time](/images/word_count_meme.jpg)

[The endlessly fascinating example of counting words in Hadoop](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-get-started-count-words.html)

--

- Cluster: name, logging
- Tags: keywords for the cluster
- **Software:** Hadoop distribution and version, pre-installed applications (Hive, Pig,...)
- File System: encryption, consistency
- **Hardware:** number and type of instances
- Security and Access: ssh keys, node access roles
- Bootstrap Actions: scripts to customize the cluster
- **Steps:** a queue of mapreduce jobs for the cluster

--

## [WordSplitter.py](https://s3.amazonaws.com/elasticmapreduce/samples/wordcount/wordSplitter.py)

<pre><code data-trim="" class="python">
#!/usr/bin/python
import sys
import re

pattern = re.compile("[a-zA-Z][a-zA-Z0-9]*")
for line in sys.stdin:
    for word in pattern.findall(line):
        print "LongValueSum:" + word.lower() + "\t" + "1"
</code></pre>

--

## Filesystems

- EMR FS vs. Hadoop FS
    - EMR FS is an implementation of HDFS, with reading and writing of files directly to S3. 
    - HDFS should be used to cache results of intermediate steps. 
- S3 and S3n
    - S3 is block-based just like HDFS. S3n is file based, which can be accessed with other tools, but filesize is limited to 5GB  
- S3 is not a file system
    - S3 has eventual consistency: files written to S3 might not be immediately available for reading. 

http://wiki.apache.org/hadoop/AmazonS3

---

# Our dataset

--

- [Digitraffic](http://www.infotripla.fi/digitraffic/doku.php?id=start_en) is a service offering real time information and data about the traffic, weather and condition information on the Finnish main roads.
- The service is provided by the [Finnish Transport Agency](http://www.liikennevirasto.fi) (*Liikennevirasto*), and produced by [Gofore](http://gofore.com) and [Infotripla](http://infotripla.fi).

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

[Static link information (271kb xml)](http://www.infotripla.fi/digitraffic/lib/exe/fetch.php?tok=a8263d&media=http%3A%2F%2Fwww.infotripla.fi%2Fdigitraffic%2Fdocs%2FLocationData.XML)

642 one-way links, 243 sites

--

```
<ivjtdata duration="60" periodstart="2014-06-24T02:55:00Z">
  <recognitions>
    <link id="110302" data_source="1">
      <recognition offset_seconds="8"  travel_time="152"></recognition>
      <recognition offset_seconds="36" travel_time="155"></recognition>
    </link>
    <link id="410102" data_source="1">
      <recognition offset_seconds="6"  travel_time="126"></recognition>
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

- **6.5** years worth of data from January 2008 to June 2014
- **3.9 million** XML files (525600 files per year)
- **6.3** GB of compressed archives (with 7.5GB of additional median data as CSV)
- **42** GB of data as XML (and 13 GB as CSV)

--

## Potential research questions

1. Does winter time have less recognitions (either due to less cars or snowy plates)?
2. Do people drive faster during the night?
3. How well number of recognitions correlate with speed (rush hour probably slows travel, but are speeds higher during days with less traffic)?
4. Is it possible to identify speed limits from the travel times? How much dispersion in speeds?
5. When do speed limits change (winter and summer limits)?

---

# Munging

--

## The small files problem

- Unpacked the tar.gz archives and uploaded the XML files as such to S3 (using AWS [CLI tools](http://aws.amazon.com/cli/)).
- Turns out small files with Hadoop is not fun [[1]](http://blog.cloudera.com/blog/2009/02/the-small-files-problem/) [[2]](http://amilaparanawithana.blogspot.fi/2012/06/small-file-problem-in-hadoop.html) [[3]](http://www.idryman.org/blog/2013/09/22/process-small-files-on-hadoop-using-combinefileinputformat-1/)
- Turns out XML is not fun either

--

## JSONify all the things!

- Concatenate data into bigger chunks
- Munging XML worth of 6.5 years takes 8.5 hours on a single t2.medium instance

--

<pre><code data-trim="" class="json">
{
  "sites": [
    {
     "id": "1205",
     "name": "Viinikka",
     "lat": 61.488282,
     "lon": 23.779057,
     "rno": "3495",
     "tro": "3495/1-2930"
    }
  ],
  "links": [
    {
      "id": "99001041",
      "name": "Hallila -> Viinikka",
      "dist": 5003.0,
      "site_start": "1108",
      "site_end": "1205"
    }]
}
</code></pre>

--

<pre><code data-trim="" class="json">
{
  "date": "2014-06-01T02:52:00Z",
  "recognitions": [
    {
      "id": "4510201",
      "tt": 117,
      "cars": 4,
      "itts": [
        100,
        139,
        121,
        110
      ]
    }
  ]
}
</code></pre>

--

## Some statistics

 - Each day was concatenated into single file
 - Each line was single minute of measurements
 - 30 days from June 2014
 - Execution time in AWS EMR 29 minutes
 - 30 mappers and 7 reducers

Comparison to local parsing:

 - Data parsed in simple python
 - Execution time: 4 minutes 46 seconds


--


## Parsing XML with Hadoop Streaming

- [Hadoop Tutorial 2.1 -- Streaming XML Files](http://cs.smith.edu/dftwiki/index.php/Hadoop_Tutorial_2.1_--_Streaming_XML_Files)
- Hadoop Streaming docs: [How do I parse XML documents using streaming?](http://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/HadoopStreaming.html#How_do_I_parse_XML_documents_using_streaming)
- [Processing XML With Hadoop Streaming](http://davidvhill.com/article/processing-xml-with-hadoop-streaming)

---

# Summary

--

[AWS EMR Best practices](https://media.amazonwebservices.com/AWS_Amazon_EMR_Best_Practices.pdf)
