
# Elastic MapReduce

###### Ville Seppänen [@Vilsepi](https://twitter.com/Vilsepi)<br>Jari Voutilainen [@Zharktas](https://twitter.com/Zharktas)<br>[@GoforeOy](https://twitter.com/GoforeOy)

---

## Agenda

1. Introduction to Hadoop Streaming and Elastic MapReduce
2. Simple Elastic MapReduce demo
3. More complex case and preprocessing of data
4. Programming Elastic MapReduce

---

## [Hadoop Streaming](http://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html)

Utility that allows running MapReduce jobs with any executable or script as the mapper and/or the reducer

<pre><code data-trim class="java">
    cat input_data.txt | mapper.py | reducer.py > output_data.txt
</code></pre>

<pre><code data-trim="" class="shell">
hadoop jar $HADOOP_HOME/hadoop-streaming.jar \
       -input   myInputDataDirectories \
       -output  myOutputDataDirectory \
       -mapper  myMapperProgram.py \
       -reducer myReducerProgram.py
</code></pre>

---

# Elastic MapReduce

--

## [Amazon Elastic MapReduce (EMR)](http://aws.amazon.com/elasticmapreduce/)

- MapReduce cluster as a service
- Managed via a web interface or API
- Can run either Amazon-optimized [Hadoop](https://docs.aws.amazon.com/ElasticMapReduce/latest/ReleaseGuide/emr-hadoop.html) or [MapR](https://www.mapr.com/)
- [Pre-installed](https://docs.aws.amazon.com/ElasticMapReduce/latest/ReleaseGuide/emr-release-components.html) Hive, Pig, Spark, Hue, Mahout, Presto...

--

## Hadoop streaming in EMR

![EMR and S3](/images/streaming-in-emr.png)

--

### For each cluster

- Hadoop version and pre-installed applications
- Computing capacity
- List of work [*steps*](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-steps.html)

*Step is a unit of work submitted to the cluster. It might contain Hadoop job(s) or instructions to install an application.*

### For each Streaming step

- Mapper and reducer program locations
- Data input and output locations

--

![Cluster creation wizard](/images/create_cluster_quick.png)

--



Cluster -> Step -> Job -> Task -> Attempt

---

# Streaming demo

--

![Say 'word count' one more time](/images/word_count_meme.jpg)

[The endlessly fascinating example of counting words in Hadoop](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-get-started-count-words.html)

--

## Cluster creation steps

- Cluster: name, logging
- Tags: keywords for the cluster
- **Software:** Hadoop distribution and version, pre-installed applications (Hive, Pig,...)
- File System: encryption, consistency
- **Hardware:** number and type of instances
- Security and Access: ssh keys, node access roles
- Bootstrap Actions: scripts to customize the cluster
- **Steps:** a queue of mapreduce jobs for the cluster

--

## [WordSplitter.py](https://s3.amazonaws.com/elasticmapreduce/samples/wordcount/wordSplitter.py) (mapper)

<pre><code data-trim="" class="python">
#!/usr/bin/python
import sys
import re

pattern = re.compile("[a-zA-Z][a-zA-Z0-9]*")
for line in sys.stdin:
    for word in pattern.findall(line):
        print "LongValueSum:" + word.lower() + "\t" + "1"
</code></pre>

<pre><code data-trim="" class="text">
LongValueSum:i         1
LongValueSum:count     1
LongValueSum:words     1
LongValueSum:with      1
LongValueSum:hadoop    1
</code></pre>

---

# Importing data

--

## Filesystems

- EMRFS is an implementation of HDFS, with reading and writing of files directly to S3.
- HDFS should be used to cache results of intermediate steps.
- S3 is block-based just like HDFS. S3n is file based, which can be accessed with other tools, but filesize is limited to 5GB

--

- S3 is not a file system, it is a RESTish object storage.
- S3 has eventual consistency: files written to S3 might not be immediately available for reading.
- EMR FS can be configured to encrypt files in S3 and monitor consistancy of files, which can detect event that try to use inconsistant files.

http://wiki.apache.org/hadoop/AmazonS3

---

# Digitraffic dataset

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
  <vehicle-recognitions>
    <link id="110302" data-source="1">
      <recognition offset="8"  travel-time="152"></recognition>
      <recognition offset="36" travel-time="155"></recognition>
    </link>
    <link id="410102" data-source="1">
      <recognition offset="6"  travel-time="126"></recognition>
      <recognition offset="45" travel-time="152"></recognition>
    </link>
    <link id="810502" data-source="1">
      <recognition offset="25" travel-time="66"></recognition>
      <recognition offset="34" travel-time="79"></recognition>
      <recognition offset="35" travel-time="67"></recognition>
      <recognition offset="53" travel-time="58"></recognition>
    </link>
  </vehicle-recognitions>
</ivjtdata>
```

Each file contains finished passthroughs for each road segment during one minute.

--

## Some numbers

- **6.5** years worth of data from January 2008 to June 2014
- **3.9 million** XML files (525600 files per year)
- **6.3** GB of compressed archives (with 7.5GB of additional median data as CSV)
- **42** GB of data as XML (and 13 GB as CSV)

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

# Programming EMR

--

## Alternatives for the web interface

- AWS [Command line tools](http://aws.amazon.com/cli/)
- SDKs like [boto](http://docs.pythonboto.org/en/latest/) for Python

--

### Connect to EMR

<pre><code data-trim="" class="python">
#!/usr/bin/env python

import boto.emr
from boto.emr.instance_group import InstanceGroup

# Requires AWS API credentials exported as env variables
connection = boto.emr.connect_to_region('eu-west-1')
</code></pre>

1 of 4

--

### Specify EC2 instances

<pre><code data-trim="" class="python">
instance_groups = []
instance_groups.append(InstanceGroup(
    role="MASTER", name="Main node",
    type="m1.medium", num_instances=1,
    market="ON_DEMAND"))
instance_groups.append(InstanceGroup(
    role="CORE", name="Worker nodes",
    type="m1.medium", num_instances=3,
    market="ON_DEMAND"))
instance_groups.append(InstanceGroup(
    role="TASK", name="Optional spot-price nodes",
    type="m1.medium", num_instances=20,
    market="SPOT", bidprice=0.012))
</code></pre>

2 of 4

--

### Start EMR cluster

<pre><code data-trim="" class="python">
cluster_id = connection.run_jobflow(
    "Our awesome cluster",
    instance_groups=instance_groups,
    action_on_failure='CANCEL_AND_WAIT',
    keep_alive=True,
    enable_debugging=True,
    log_uri="s3://bucket/logs/",
    ami_version="3.3.1",
    bootstrap_actions=[],
    ec2_keyname="name-of-our-ssh-key",
    visible_to_all_users=True,
    job_flow_role="EMR_EC2_DefaultRole",
    service_role="EMR_DefaultRole")
</code></pre>

3 of 4

--

### Add work step to cluster

<pre><code data-trim="" class="python">
steps = []
steps.append(boto.emr.step.StreamingStep(
    "Our awesome streaming app",
    input="s3://bucket/our-input-data",
    output="s3://bucket/our-output-path/",
    mapper="our-mapper.py",
    reducer="aggregate",
    cache_files=[
        "s3://bucket/programs/our-mapper.py#our-mapper.py",
        "s3://bucket/data/our-dictionary.json#our-dictionary.json",)
        ],
    action_on_failure='CANCEL_AND_WAIT',
    jar='/home/hadoop/contrib/streaming/hadoop-streaming.jar'))
connection.add_jobflow_steps(cluster_id, steps)
</code></pre>

4 of 4

--

### Recap

<pre><code data-trim="" class="python">
import boto.emr
from boto.emr.instance_group import InstanceGroup

# Create a connection to AWS
connection = boto.emr.connect_to_region('eu-west-1')

# Create a new EMR cluster
cluster_id = connection.run_jobflow(**cluster_parameters)

# Add steps to the cluster
connection.add_jobflow_steps(cluster_id, **steps_parameters)
</code></pre>

---

## Analyzing the Digitraffic dataset

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
  carspeeds.py
  digitraffic/munged/links-by-month/2014

Step will output data to
  s3://hadoop-seminar-emr/digitraffic/outputs/carspeeds.py/
</code></pre>

--

## Step 2 of 2: Analyze results

<pre><code data-trim="" class="python">
# Download and concatenate output
aws s3 cp
  s3://hadoop-seminar-emr/digitraffic/outputs/carspeeds.py/
  /tmp/emr
  --recursive
  --profile hadoop-seminar-emr

cat /tmp/emr/part-* > /tmp/emr/output
</code></pre>

<pre><code data-trim="" class="bash">
# Analyze results
05-car-speed-for-time-of-day_output.py
  /tmp/emr/output
  example-data/locationdata.json
</code></pre>

--

![Average car speeds per time of day](/images/graphs.png)

--

![EC2 console](/images/ec2-console.png)

--

## Conclusions about the dataset

- We only used subset of whole dataset due to interest in EMR instead of analyzing the data
- EMR/Hadoop creates overhead which are substantial with small files
- Even after munging files together, our subset took considerably longer in EMR compared to local parsing
- "Too small problem for EMR/Hadoop"

---

# Summary

--

## Takeaways

- Make sure your problem is big enough for Hadoop
- Munging wisely makes streaming programs easier and faster
- Always use Spot instances with EMR

--

## Further reading

Presentation and source code are available at  
[https://github.com/gofore/aws-emr](https://github.com/gofore/aws-emr)

- [Amazon EMR Developer Guide](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-what-is-emr.html)
- [Amazon EMR Best practices](https://media.amazonwebservices.com/AWS_Amazon_EMR_Best_Practices.pdf)
- [Scaling a 2000-node Hadoop cluster on EC2](https://maas.ubuntu.com/2012/06/04/scaling-a-2000-node-hadoop-cluster-on-ec2ubuntu-with-juju/)
- [Quiz: Is it a Pokemon or a bigdata technology?](http://www.slate.com/blogs/future_tense/2014/05/02/big_data_borat_tests_people_on_pok_mon_versus_big_data_technology_names.html)
