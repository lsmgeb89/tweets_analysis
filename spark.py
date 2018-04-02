import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext


# Create a local StreamingContext with four working thread and batch interval of 2 second
sc = SparkContext(master="local[2]", appName="Tweets Sentiment Analysis")
ssc = StreamingContext(sc, 4)
ssc.checkpoint("tsa")

# Create a DStream that will connect to localhost:9001
data_stream = ssc.socketTextStream("localhost", 9001)

# transform
data_stream.map(lambda s: json.loads(s.decode("utf-8")))
data_stream.pprint()

# Start the computation
ssc.start()

# Wait for the computation to terminate
ssc.awaitTermination()
