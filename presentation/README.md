
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

# EMR demo

--

![Say 'word count' one more time](/images/word_count_meme.jpg)

[The endlessly fascinating example of counting words in Hadoop](http://docs.aws.amazon.com/ElasticMapReduce/latest/DeveloperGuide/emr-get-started-count-words.html)

--

Cluster Configuration: name, logging
Tags: keywords for the cluster
Software Configuration: Hadoop version, Hive, Pig, HBase, Ganglia...
File System Configuration: EMRFS file encryption, consistency
Hardware Configuration: master, code and task nodes
Security and Access: ssh keys, node access roles
Bootstrap Actions: scripts to initialize the cluster
Steps: a queue of jobs of the cluster

---

# Our dataset

--

[Digitraffic](http://www.infotripla.fi/digitraffic/doku.php?id=start_en) is a service offering real time information and data about the traffic, weather and condition information on the Finnish main roads.

The service is provided by the [Finnish Transport Agency](http://www.liikennevirasto.fi).

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
