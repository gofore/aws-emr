
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

--

- S3 is not a file system
- S3 has eventual consistency: files written to S3 might not be immediately available for reading. 
- EMR FS can be configured to encrypt files in S3 and monitor consistancy of files, which can detect event that try to use inconsistant files.

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

1. Do people drive faster during the night?
2. Does winter time have less recognitions (either due to less cars or snowy plates)?
3. How well number of recognitions correlate with speed (rush hour probably slows travel, but are speeds higher during days with less traffic)?
4. Is it possible to identify speed limits from the travel times? How much dispersion in speeds?
5. When do speed limits change (winter and summer limits)?

---

# Munging

--

## The small files problem

- Unpacked the tar.gz archives and uploaded the XML files as such to S3 (using AWS [CLI tools](http://aws.amazon.com/cli/)).
- Turns out (4 million 11kB) small files with Hadoop is not fun. Hadoop does not handle well with files significantly smaller than the HDFS block size (default 64MB) [[1]](http://blog.cloudera.com/blog/2009/02/the-small-files-problem/) [[2]](http://amilaparanawithana.blogspot.fi/2012/06/small-file-problem-in-hadoop.html) [[3]](http://www.idryman.org/blog/2013/09/22/process-small-files-on-hadoop-using-combinefileinputformat-1/)
- And well, XML is not fun either, so...

--

## JSONify all the things!

- Wrote scripts to parse, munge and upload data
- Concatenated data into bigger files, calculated some extra data, and converted it into JSON. Size reduced to 60% of the original XML.
- First munged 1-day files (10-20MB each) and later 1-month files (180-540MB each)
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
Static link information (120kb json)

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

---

# Running EMR via boto

--

## Write a bunch of tools...

- boto

--

## Step 1 of 2: Run mapreduce

<pre><code data-trim="" class="bash">
# Create new cluster
aws-tools/run-jobs.py
  create-cluster
  "Car speed counting cluster"

Starting cluster
  j-F0K0A4Q9F5O0 Car speed counting cluster
</code></pre>

<pre><code data-trim="" class="bash">
# Add job step to the cluster
aws-tools/run-jobs.py
  run-step
  j-F0K0A4Q9F5O0
  05-car-speed-for-time-of-day_map.py
  digitraffic/munged/links-by-month/2014

Step will output data to
  s3://hadoop-seminar-emr/digitraffic/outputs/
  2015-02-18_11-08-24_05-car-speed-for-time-of-day_map.py/
</code></pre>

--

## Step 2 of 2: Analyze results

<pre><code data-trim="" class="bash">
# Download and concatenate output
aws s3 cp 
  s3://hadoop-seminar-emr/digitraffic/outputs/2015-02-18_11-08-24_05-car-speed-for-time-of-day_map.py/
  /tmp/emr 
  --recursive 
  --profile hadoop-seminar-emr

cat /tmp/emr/part-* > /tmp/emr/output
</code></pre>
<pre><code data-trim="" class="bash">
# Analyze results
result-analysis/05_speed_during_day/05-car-speed-for-time-of-day_output.py
  /tmp/emr/output 
  example-data/locationdata.json
</code></pre>

--

![Average car speeds per time of day](/images/graphs.png)

--

![EC2 console](/images/ec2-console.png)

--

## Some statistics

- We experimented with different input files an cluster sizes
- Execution time was about half hour with small cluster and 30 small 15-20 MB files
- Same input parsed with simple python script took about 5 minutes 

- Larger cluster and 6 larger 500 MB files took 17 minutes.

"Too small problem for EMR/Hadoop"

---

# Summary

--

## Takeaways

- Make sure your problem is big enough for Hadoop
- Munging wisely makes streaming programs easier and faster
- Always use Spot instances with EMR

--

## Further reading

- [AWS EMR Best practices](https://media.amazonwebservices.com/AWS_Amazon_EMR_Best_Practices.pdf)
- Ubuntu MaaS blog: [Scaling a 2000-node Hadoop cluster on EC2](https://maas.ubuntu.com/2012/06/04/scaling-a-2000-node-hadoop-cluster-on-ec2ubuntu-with-juju/)
- Big Data Borat: *["Quiz: Is it a Pokemon or a bigdata technology?"](http://www.slate.com/blogs/future_tense/2014/05/02/big_data_borat_tests_people_on_pok_mon_versus_big_data_technology_names.html)*
