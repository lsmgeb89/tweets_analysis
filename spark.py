import json
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
from pyspark import SparkContext
from pyspark.streaming import StreamingContext

nltk.download('punkt')
nltk.download('vader_lexicon')

# Create a local StreamingContext with four working thread and batch interval of 2 second
sc = SparkContext(master="local[2]", appName="Tweets Sentiment Analysis")
ssc = StreamingContext(sc, 4)
ssc.checkpoint("tsa")

# Create a DStream that will connect to localhost:9001
data_stream = ssc.socketTextStream("localhost", 9001)


# Use Vader to analyze sentiment
def sentiment_analysis(js):
    sentences = tokenize.sent_tokenize(js["tweet"])
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


# transform
data_stream.map(lambda s: json.loads(s)).map(sentiment_analysis).pprint()

# Start the computation
ssc.start()

# Wait for the computation to terminate
ssc.awaitTermination()
