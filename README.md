# Readme

## Setup

### Install Elasticsearch and Kibana
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

sudo apt-get update
sudo apt -y install elasticsearch kibana

### Install Elasticsearch-Hadoop
https://www.elastic.co/downloads/hadoop

### Install python packages
sudo apt install python3-pip
sudo -H pip install --upgrade pip
sudo -H pip3 install --upgrade pip
sudo -H pip3 install tweepy pyspark googlemaps nltk twython elasticsearch numpy

### Set up keys
export G_MAPS_API_KEY=<api_key>
export T_ACCESS_TOKEN=<access_token>
export T_ACCESS_SECRET=<access_secret>
export T_CONSUMER_KEY=<consumer_key>
export T_CONSUMER_SECRET=<consumer_secret>

### Start services
sudo systemctl start elasticsearch
sudo systemctl start kibana

### Check services
sudo systemctl status elasticsearch
sudo systemctl status kibana

### Monitor elasticsearch
chromium-browser http://localhost:9200 &

### Monitor kibana
chromium-browser http://localhost:5601 &

### Run server
python3 stream.py <server_port> <hash_tag>
python3 stream.py 9001 Trump

### Run client
spark-submit --jars <path/to/elasticsearch_hadoop_jar_file> spark.py <es_domain> <es_port> <server_port> <interval>
spark-submit --jars /home/sliu/frameworks/elasticsearch-hadoop-6.2.3/dist/elasticsearch-hadoop-6.2.3.jar spark.py localhost 9200 9001 10

### Check documents in the index (tweets) and type (tweet)
curl -XGET 'localhost:9200/tweets/tweet/_search?pretty'

### Delete index (tweets)
curl -XDELETE 'localhost:9200/tweets'
