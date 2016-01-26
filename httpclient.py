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

def testPOST():
    args = {'a':'aaaaaaaaaaaaa',
            'b':'bbbbbbbbbbbbbbbbbbbbbb',
            'c':'c',
            'd':'012345\r67890\n2321321\n\r'}
    url = "http://www.httpbin.org/post"

    http = HTTPClient()
    r = http.POST(url, args)
    print r.code
    print r.body

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port=80):
        # use sockets!
        # init socket obj & connect to host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print host
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
        patern = r"\r?\n\r?\n"
        return re.split(patern, data)[-1]

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

    def parse_url(self, url):
        # cut http:// cause Tim Berners-Lee
        if url.find("http://") != -1:
            url = url[url.index("//")+2:]

        # add slash if needed eg: slashdot.org +"/"
        if url.find("/") == -1:
            url += "/"

        port = re.search(r':([0-9]+)\/', url)
        if port:
            url = url.replace(":"+port.group(1), "")
            port = int(port.group(1))
        else:
            port = 80

        return url, port

    def GET(self, url, args=None):
        url, port = self.parse_url(url)
        # build post and host header
        self.request =  "GET " + url[url.index("/"):] + " HTTP/1.0\n" + \
                        "Host: " + url[:url.index("/")] + "\n\n"

        # form connection obj and connect
        sock = self.connect(url[:url.index("/")], port)
        data = self.recvall(sock)

        # format response into object
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url, port = self.parse_url(url)

        # build post and host header
        self.request =  "POST " + url[url.index("/"):] + " HTTP/1.0\n" + \
                        "Host: " + url[:url.index("/")] + "\n" + \
                        "Content-Type: application/x-www-form-urlencoded\n"
        # add args into the header & content length
        # since we get the args in a dict
        if args:
            form_args = ""
            for i in range(len(args.keys())):
                    form_args += args.keys()[i] + "=" + \
                                args.values()[i] + "&"
            self.request += "Content-Length: {}\n\n".format(str(len(form_args)))
            self.request += r"".join(form_args)

            self.request = self.request.rstrip("&")

        # add in terminating newline
        self.request +=  "\n"

        print self.request

        # form connection obj and connect
        sock = self.connect(url[:url.index("/")], port)
        data = self.recvall(sock)

        # format response into object
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):
        testPOST()
    elif (len(sys.argv) == 3):
        r = client.command(sys.argv[2], sys.argv[1])
        print r.code
        print r.body
    else:
        r = client.command(sys.argv[1])
        print r.code
