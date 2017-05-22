from __future__ import print_function
import optparse
from proton.handlers import MessagingHandler
from proton.reactor import Container


import socketserver
import random
import time
from queue import Queue
from threading import Thread

# Maximum number of pending events
MAX_QUEUE_SIZE = 100
# Where to run the server
HOST = '0.0.0.0'
PORT = 9999

# The time between generated events
EVENT_PERIOD_SECONDS = 1
# Fake data for random events
datas = ['{}'.format(i) for i in range(1)]

class Recv(MessagingHandler):
    def __init__(self, url, count):
        super(Recv, self).__init__()
        self.url = url
        self.expected = count
        self.received = 0

    def on_start(self, event):
        event.container.create_receiver(self.url)

    def on_message(self, event):
        if event.message.id and event.message.id < self.received:
            # ignore duplicate message
            return
        if self.expected == 0 or self.received < self.expected:
            print(event.message.body)
            self.received += 1
            if self.received == self.expected:
                event.receiver.close()
                event.connection.close()

parser = optparse.OptionParser(usage="usage: %prog [options]")
parser.add_option("-a", "--address", default="localhost:5672/examples",help="address from which messages are received (default %default)")
parser.add_option("-m", "--messages", type="int", default=100,help="number of messages to receive; 0 receives indefinitely (default %default)")
opts, args = parser.parse_args()


def generate_event(datas):
    data = random.choice(datas)
    
    print ("Generated data",data)
    return '{}'.format(data)


def run_server(host, port, queue):
    """Run a SocketServer.TCPServer on host, port which writes strings from
    queue to the socket as they become available.
    """
    class QueueTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            while True:
                line = queue.get()
                self.request.sendall(str.encode(line))
                print ("Sent data:",line)

    server = socketserver.TCPServer((host, port), QueueTCPHandler)
    server.serve_forever()

if __name__ == '__main__':
    input_queue = Queue(maxsize=MAX_QUEUE_SIZE)

    server_thread = Thread(target=run_server, args=(HOST, PORT, input_queue,))
    server_thread.daemon = True
    server_thread.start()
    print ("Started server")

    while True:
        input_queue.put(generate_event(datas) + '\n')
        try:
                Container(Recv(opts.address, opts.messages)).run()
        except KeyboardInterrupt: pass
        time.sleep(EVENT_PERIOD_SECONDS)
