from elasticsearch import Elasticsearch
import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from pyspark import SparkContext
from pyspark.streaming import StreamingContext


es = Elasticsearch(["http://localhost:9200"])
index_name = "tweets"
doc_type = "tweet"
es_write_conf = {
    "es.nodes": "localhost",
    "es.port": "9200",
    "es.resource": index_name + "/" + doc_type
}


def create_index():
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

    if not es.indices.exists(index_name):
        res = es.indices.create(index=index_name, body=index_mapping)
        print(res)


class SparkStream:

    def __init__(self):

        # Create a local StreamingContext with four working thread and batch interval of 2 second
        self.sc = SparkContext(master="local[2]", appName="Tweets Sentiment Analysis")
        self.ssc = StreamingContext(self.sc, 4)
        self.ssc.checkpoint("tsa")

        # Create a DStream that will connect to localhost:9001
        self.data_stream = self.ssc.socketTextStream("localhost", 9001)

    def register_transform(self):

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

            if avg >= 0.5:
                js['sentiment'] = 'positive'
            elif avg >= -0.5:
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
    nltk.download('punkt')
    nltk.download('vader_lexicon')

    create_index()

    stream = SparkStream()
    stream.register_transform()
    stream.start_stream()


if __name__ == "__main__":
    main()
