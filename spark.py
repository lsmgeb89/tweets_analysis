from elasticsearch import Elasticsearch
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import sys


index_name = "tweets"
doc_type = "tweet"


def create_index(domain, port):
    es = Elasticsearch(["http://" + domain + ":" + port])
    index_mapping = {
        "mappings": {
            doc_type: {
                "properties": {
                    "message": {"type": "text"},
                    "sentiment": {"type": "text"},
                    "location": {"type": "geo_point"},
                    "timestamp": {"type": "date"}
                }
            }
        }
    }

    if es.indices.exists(index_name):
        res = es.indices.delete(index_name)
        print(res)

    res = es.indices.create(index=index_name, body=index_mapping)
    print(res)


class SparkStream:

    def __init__(self, server_port, interval):

        # Create a local StreamingContext with four working thread and batch interval of 10 second
        self.sc = SparkContext(master="local[4]", appName="Tweets Sentiment Analysis")
        self.ssc = StreamingContext(self.sc, interval)
        self.ssc.checkpoint("tsa")

        # Create a DStream that will connect to localhost:9001
        self.data_stream = self.ssc.socketTextStream("localhost", server_port)

    def register_transform(self, domain, port):

        es_write_conf = {
            "es.nodes": domain,
            "es.port": port,
            "es.resource": index_name + "/" + doc_type
        }

        # Use Vader to analyze sentiment
        def sentiment_analysis(js):
            sentences = tokenize.sent_tokenize(js["message"])
            sid = SentimentIntensityAnalyzer()

            total = 0
            count = 0
            for sentence in sentences:
                ss = sid.polarity_scores(sentence)
                total += ss['compound']
                count += 1
            avg = total / count

            if avg >= 0.35:
                js['sentiment'] = 'positive'
            elif avg >= -0.35:
                js['sentiment'] = 'neutral'
            else:
                js['sentiment'] = 'negative'

            return js

        def send_data_to_es(data):
            data.saveAsNewAPIHadoopFile(
                path="-",
                outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
                keyClass="org.apache.hadoop.io.NullWritable",
                valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
                conf=es_write_conf)

        self.data_stream\
            .map(lambda s: json.loads(s))\
            .map(sentiment_analysis)\
            .map(lambda x: (None, x))\
            .foreachRDD(send_data_to_es)

    def start_stream(self):
        # Start the computation
        self.ssc.start()

        # Wait for the computation to terminate
        self.ssc.awaitTermination()


def main():
    if len(sys.argv) != 5:
        print("Usage:", sys.argv[0], "<es_domain> <es_port> <server_port> <interval>", file=sys.stderr)
        sys.exit(-1)

    nltk.download('punkt')
    nltk.download('vader_lexicon')

    es_domain = str(sys.argv[1])
    es_port = str(sys.argv[2])
    create_index(es_domain, es_port)

    server_port = int(sys.argv[3])
    interval = int(sys.argv[4])
    stream = SparkStream(server_port, interval)
    stream.register_transform(es_domain, es_port)
    stream.start_stream()


if __name__ == "__main__":
    main()
