import googlemaps
import json
import os
from pprint import pprint
import re
import signal
import socket
import sys
import threading
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
    stop = False
    stop_lock = threading.Lock()

    def __init__(self, conn):
        super(TweetsListener, self).__init__()
        self.conn = conn
        self.g_maps = googlemaps.Client(os.environ.get("G_MAPS_API_KEY"))

    def on_status(self, status):
        with TweetsListener.stop_lock:
            if TweetsListener.stop is True:
                print("on_status returns false to stop streaming")
                self.conn.close()
                return False

        # only deal with english tweets
        if status.lang is not None and status.lang != "en":
            return True

        msg_dict = {"message": None, "location": None, "timestamp": None}

        if status.text is not None:
            # try to get full tweet
            try:
                text = status.extended_tweet["full_text"]
            except AttributeError:
                text = status.text

            # remove emoji
            emoji_pattern = re.compile("["
                                        u"\U0001F600-\U0001F64F"
                                        u"\U0001F300-\U0001F5FF"
                                        u"\U0001F680-\U0001F6FF"
                                        u"\U0001F1E0-\U0001F1FF"
                                        "]+", flags=re.UNICODE)
            no_emoji_str = emoji_pattern.sub(r'', text)

            # remove url
            url_pattern = re.compile(r'(http[s]://[\w./]+)*')
            msg_dict["message"] = url_pattern.sub(r'', no_emoji_str)

        if status.user.location is not None:
            geocode_result = self.g_maps.geocode(status.user.location)
            if len(geocode_result) == 1:
                msg_dict["location"] = geocode_result[0]["geometry"]["location"]
                msg_dict["location"]["lon"] = msg_dict["location"].pop("lng")

        if status.created_at is not None:
            msg_dict["timestamp"] = status.created_at.isoformat()

        pprint(msg_dict)
        print()

        # need \n as termination char
        self.conn.send(json.dumps(msg_dict).encode("utf-8") + b"\n")
        return True

    def on_error(self, status_code):
        if status_code == 420:
            return False
        else:
            print(status_code)

    @staticmethod
    def signal_handler(sig, frame):
        print("Receive Ctrl-C and stop streaming:", file=sys.stderr)
        with TweetsListener.stop_lock:
            TweetsListener.stop = True


class TweetsStream:

    def __init__(self, conn):
        self.auth = tweepy.OAuthHandler(os.environ.get("T_CONSUMER_KEY"),
                                        os.environ.get("T_CONSUMER_SECRET"))
        self.auth.set_access_token(os.environ.get("T_ACCESS_TOKEN"),
                                   os.environ.get("T_ACCESS_SECRET"))
        self.listener = TweetsListener(conn)
        self.stream = tweepy.Stream(auth=self.auth, listener=self.listener, tweet_mode="extended")

    def start(self, hash_tag):
        signal.signal(signal.SIGINT, self.listener.signal_handler)
        self.stream.filter(track=[hash_tag])


def main():
    if len(sys.argv) != 3:
        print("Usage:", sys.argv[0], "<server_port> <hash_tag>", file=sys.stderr)
        sys.exit(-1)

    server = SocketServer()
    conn = server.setup("localhost", int(sys.argv[1]))

    stream = TweetsStream(conn)
    hash_tag = "#" + str(sys.argv[2])
    stream.start(hash_tag)


if __name__ == "__main__":
    main()
