# Tweets Sentiment Analysis

## Summary

* Built a real-time tweets sentiment analysis application using Python, [Spark Streaming][spark_stream], [Elasticsearch][es] and [Kibana][kibana]
* Implemented a scrapper that collects and pre-processes tagged tweets for analytics and served as a [Spark Streaming][spark_stream] source
* Implemented real-time sentiment analysis by using NLTK and [Spark Streaming][spark_stream] that served as a source for data visualization
* Created a visualization panel including data table and heatmaps to show the geolocation distribution of sentiment analysis results by using [Elasticsearch][es] and [Kibana][kibana]

## Project Information

* Course: Big Data Management and Analytics (CS 6350)
* Professor: [Latifur Khan][khan]
* Semester: Spring 2018
* Programming Language: Python 3

## Setup on Ubuntu

### Install Elasticsearch and Kibana

* `echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list`
* `wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -`
* `sudo apt-get update`
* `sudo apt -y install elasticsearch kibana`

### Install Elasticsearch-Hadoop

* Download and install [ES-Hadoop][es_hadoop]

### Install Python Packages

* `sudo apt install python3-pip`
* `sudo -H pip install --upgrade pip`
* `sudo -H pip3 install --upgrade pip`
* `sudo -H pip3 install tweepy pyspark googlemaps nltk twython elasticsearch numpy`

### Set Up Twitter API Keys and Tokens

* Get Twitter API Keys and tokens from [Twitter Apps][twitter_app]
* `export T_ACCESS_TOKEN=<access_token>`
* `export T_ACCESS_SECRET=<access_secret>`
* `export T_CONSUMER_KEY=<consumer_key>`
* `export T_CONSUMER_SECRET=<consumer_secret>`

### Set UP Google Maps Geolocation API Key

* Get Google Maps Geolocation API Key from [Google][google_app]
* `export G_MAPS_API_KEY=<api_key>`

### Start Services

* `sudo systemctl start elasticsearch`
* `sudo systemctl start kibana`

### Check Services

* `sudo systemctl status elasticsearch`
* `sudo systemctl status kibana`

### Monitor Elasticsearch

* `chromium-browser http://localhost:9200 &`

### Monitor kibana

* `chromium-browser http://localhost:5601 &`

### Run Server

* `python3 stream.py <server_port> <hash_tag>`
* i.e. `python3 stream.py 9001 Trump`

### Run Client

* `spark-submit --jars <path/to/elasticsearch_hadoop_jar_file> spark.py <es_domain> <es_port> <server_port> <interval>`
* i.e. `spark-submit --jars ${HOME}/frameworks/elasticsearch-hadoop-6.2.3/dist/elasticsearch-hadoop-6.2.3.jar spark.py localhost 9200 9001 10`

### Check Documents in the Index (`tweets`) and Type (`tweet`)

* `curl -XGET 'localhost:9200/tweets/tweet/_search?pretty'`

### Delete Index (`tweets`)

* `curl -XDELETE 'localhost:9200/tweets'`

## Reference

### NLTK

* [Sentiment Analysis][nltk_sentiment]

### Google Maps API

* [Geocoding API][geocoding]

### Tweepy

* [Tweepy Streaming][tweepy_stream]
* [Tweepy Response Sample][res_sample]

### Spark

* [Writing to ES Index][write_to_es]
* [Pyspark Stream Example][pyspark_stream]
* [Graceful Shutdown Example][graceful_shutdown]

### Elasticsearch

* [Create ES Index][create_es_index]
* [Elasticsearch Document][es_doc]

### Kibana

* [Kibana Document][kibana_doc]

[khan]: https://cs.utdallas.edu/people/faculty/khan-latifur/
[spark_stream]: https://spark.apache.org/streaming/
[es]: https://www.elastic.co/
[kibana]: https://www.elastic.co/products/kibana
[es_hadoop]: https://www.elastic.co/downloads/hadoop
[twitter_app]: https://apps.twitter.com/
[google_app]: https://developers.google.com/maps/documentation/geolocation/get-api-key
[nltk_sentiment]: http://www.nltk.org/howto/sentiment.html
[geocoding]: https://developers.google.com/maps/documentation/geocoding/start
[tweepy_stream]: http://docs.tweepy.org/en/v3.6.0/streaming_how_to.html
[res_sample]: https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2
[write_to_es]: https://db-blog.web.cern.ch/blog/prasanth-kothuri/2016-05-integrating-hadoop-and-elasticsearch-%E2%80%93-part-2-%E2%80%93-writing-and-querying
[pyspark_stream]: https://github.com/apache/spark/blob/master/examples/src/main/python/streaming/network_wordcount.py
[graceful_shutdown]: https://github.com/lanjiang/streamingstopgraceful/blob/master/src/main/scala/com/cloudera/ps/GracefulShutdownExample.scala
[create_es_index]: https://stackoverflow.com/questions/45305721/pyspark-error-writing-dstream-to-elasticsearch
[es_doc]: https://www.elastic.co/guide/en/elasticsearch/guide/current/index.html
[kibana_doc]: https://www.elastic.co/guide/en/kibana/current/index.html
