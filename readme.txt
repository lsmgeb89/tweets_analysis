sudo apt install python3-pip
sudo -H pip install --upgrade pip
sudo -H pip3 install --upgrade pip
sudo -H pip3 install tweepy pyspark googlemaps nltk twython

export PYSPARK_PYTHON=python3

python3 stream.py Trump
python3 spark.py
