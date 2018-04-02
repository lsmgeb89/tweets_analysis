import googlemaps
import json
import os
from pprint import pprint
import socket
import sys
import tweepy


class SocketServer:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def setup(self, host, port):
        self.sock.bind((host, port))
        self.sock.listen(1)
        conn, address = self.sock.accept()
        return conn


class TweetsListener(tweepy.StreamListener):

    def __init__(self, conn):
        tweepy.StreamListener.__init__(self)
        self.conn = conn
        self.g_maps = googlemaps.Client(os.environ.get("G_MAPS_API_KEY"))

    def on_status(self, status):
        msg_dict = {"tweet": None, "location": None, "timestamp": None}

        if status.text is not None:
            msg_dict["tweet"] = status.text

        if status.user.location is not None:
            geocode_result = self.g_maps.geocode(status.user.location)
            if len(geocode_result) == 1:
                msg_dict["location"] = geocode_result[0]["geometry"]["location"]

        if status.created_at is not None:
            msg_dict["timestamp"] = status.created_at.isoformat()

        pprint(msg_dict)
        print("\n")

        # need \n as termination char
        self.conn.send(json.dumps(msg_dict).encode("utf-8") + b"\n")

    def on_error(self, status_code):
        if status_code == 420:
            return False
        else:
            print(status_code)


class TweetsStream:

    def __init__(self, conn):
        self.auth = tweepy.OAuthHandler(os.environ.get("T_CONSUMER_KEY"),
                                        os.environ.get("T_CONSUMER_SECRET"))
        self.auth.set_access_token(os.environ.get("T_ACCESS_TOKEN"),
                                   os.environ.get("T_ACCESS_SECRET"))
        self.stream = tweepy.Stream(self.auth, TweetsListener(conn))

    def start(self, hash_tag):
        self.stream.filter(track=[hash_tag])


def main():
    if len(sys.argv) != 2:
        print("Usage: stream.py <hash_tag>", file=sys.stderr)
        sys.exit(-1)

    hash_tag = "#" + str(sys.argv[1])

    server = SocketServer()
    conn = server.setup("localhost", 9001)

    stream = TweetsStream(conn)
    stream.start(hash_tag)


if __name__ == "__main__":
    main()
