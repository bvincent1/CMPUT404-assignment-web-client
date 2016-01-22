#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port=80):
        # use sockets!
        # init socket obj & connect to host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        sock.sendall(self.request)

        return sock

    # Returns response status code as int
    def get_code(self, data):
        patern = r"[0-9]{3}"
        return int(re.search(patern, data).group(0))

    # Returns response headers as an arry of strings with /r and /n removed
    def get_headers(self,data):
        patern = r"(.+:\s.+)"
        return [i.rstrip("\r").rstrip("\n") for i in re.findall(patern, data)]

    # Returns response body as a string with newlines
    def get_body(self, data):
        patern = r"(\r\n){2}|(\n){2}"
        return str(re.split(patern, data)[-1])

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(2048)
            if (part):
                buffer.extend(part)
            else:
                done = True
        return str(buffer)

    def GET(self, url, args=None):
        # cut http:// cause Tim Berners-Lee
        if url.find("http://") != -1:
            url = url[url.index("//")+2:]

        if url.find("/") == -1:
            url += "/"

        # build post and host header
        self.request =  "GET " + url[url.index("/"):] + " HTTP/1.0\n" + \
                        "Host: " + url[:url.index("/")] + "\n\n"

        sock = self.connect(url[:url.index("/")])
        data = self.recvall(sock)

        # format response into object
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        # cut http:// cause Tim Berners-Lee
        if url.find("http://") != -1:
            url = url[url.index("//")+2:]

        if url.find("/") == -1:
            url += "/"

        # build post and host header
        self.request =  "POST " + url[url.index("/"):] + " HTTP/1.0\n" + \
                        "Host: " + url[:url.index("/")] + "\n\n" + args
        # add args into the header
        # since we get the args in a dict
        list_args = [ key + ": " + value for key in args.keys() for value in args.values()]

        for arg in list_args:
            self.request += arg + "\n"

        # format response into object
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        r = client.command(sys.argv[2], sys.argv[1])
        print r.code
    else:
        r = client.command(sys.argv[1])
        print r.code
