sudo apt install python3-pip
sudo -H pip install --upgrade pip
sudo -H pip3 install --upgrade pip
sudo -H pip3 install tweepy pyspark googlemaps nltk twython elasticsearch

python3 stream.py 9001 Trump
spark-submit --jars elasticsearch-hadoop-6.2.3.jar spark.py localhost 9200 9001 10
