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
        request = "GET / HTTP/1.0\n\n"

        # init socket obj & connect to host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host,port))
        sock.sendall(request)

        return sock

    # Returns status code
    def get_code(self, data):
        patern = r"[0-9]{3}"
        return re.search(patern, data).group(0)

    # Returns headers as an arry of strings with /r and /n removed
    def get_headers(self,data):
        patern = r"(.+:\s.+)"
        return [i.rstrip("\r").rstrip("\n") for i in re.findall(patern, data)]

    # Returns body as a string with newlines
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
        sock = self.connect(url)
        data = self.recvall(sock)

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = "POST / HTTP/1.0\n\n"
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(sys.argv[1])
