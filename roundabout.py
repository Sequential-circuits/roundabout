from __future__ import print_function, unicode_literals
import optparse
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import sys


class Send(MessagingHandler):
    def __init__(self, url, messages):
        super(Send, self).__init__()
        self.url = url
        self.sent = 0
        self.confirmed = 0
        self.total = messages

    def on_start(self, event):
        self.acceptor = event.container.listen(self.url)

    def on_sendable(self, event):
        while event.sender.credit and self.sent < self.total:
            msg = Message(id=(self.sent+1), body={'sequence':(self.sent+1)})
            event.sender.send(msg)
            self.sent += 1

    def on_accepted(self, event):
        self.confirmed += 1
        if self.confirmed == self.total:
            print("Messages sent")
            event.connection.close()
            self.acceptor.close()

    def on_disconnected(self, event):
        self.sent = self.confirmed

parser = optparse.OptionParser(usage="usage: %prog [options]",description="Send messages to the supplied address.")
parser.add_option("-a", "--address", default="localhost:5672/examples",help="address to which messages are sent (default %default)")
parser.add_option("-m", "--messages", type="int", default=100,help="number of messages to send (default %default)")
opts, args = parser.parse_args()

def quiet_logs( sc ):
  logger = sc._jvm.org.apache.log4j
  logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
  logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )

def sendRecord(tup):
    try:
        Container(Send(opts.address, opts.messages)).run()
    except KeyboardInterrupt: pass
    print ("Sent message back to car")
    
if __name__ == "__main__":
    conf = SparkConf().setAppName("using foreachRDD and foreach on RDD")
    sc   = SparkContext(conf=conf)
    ssc  = StreamingContext(sc, 2)
    ssc.checkpoint("checkpoint")
    
    quiet_logs(sc)
    
    # Create a DStream that will connect to hostname:port, like localhost:9999
    lines = ssc.socketTextStream("localhost", 9999)
    # lines = ssc.textFileStream('./streamingData')

    # Split each line into words
    words = lines.flatMap(lambda line: line.split(" "))

    # Count each word in each batch
    pairs = words.map(lambda word: (word, 1))

    wordCounts = pairs.reduceByKey(lambda x, y: x + y)

    # http://spark.apache.org/docs/latest/streaming-programming-guide.html#design-patterns-for-using-foreachrdd
    wordCounts.foreachRDD(lambda rdd: rdd.foreach(sendRecord))
       
    wordCounts.pprint()
    
    ssc.start()             # Start the computation
    ssc.awaitTermination()  # Wait for the computation to terminate
