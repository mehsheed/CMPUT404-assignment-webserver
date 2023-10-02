#  coding: utf-8
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def create_html_template_error(self, status_code):
        if status_code == 404:
            response_body = """<!DOCTYPE html>
                                <html>
                                <head>
                                    <title>404 - Page Not Found</title>
                                </head>
                                <body>
                                    <h1>404 - Page Not Found</h1>
                                    <p>The page you are looking for does not exist.</p>
                                </body>
                                </html> \n"""
            body_len = str(len(response_body))
            return response_body, body_len
        elif status_code == 405:
            response_body = """<!DOCTYPE html>
                                <html>
                                <head>
                                    <title>405 - Method Not Allowed</title>
                                </head>
                                <body>
                                    <h1>405 - Method Not Allowed</h1>
                                    <p>The method you are using is not allowed.</p>
                                </body>
                                </html> \n"""
            body_len = str(len(response_body))
            return response_body, body_len

    def create_response(self, file_path, file_type, status_code):
        # Create a response header
        response_header = ""
        response_body = ""
        response = ""
        # Create a response body
        if status_code == 200:
            f = open(file_path, "r")
            response_body = f.read()

            # genreate response header
            response = (
                "HTTP/1.1 200 OK\r\n"
                + "Content-Type: "
                + file_type
                + "\r\n"
                + "Content-Length: "
                + str(len(response_body))
                + "\r\n"
                + "Connection: close\r\n\r\n"
                + response_body
            )
            f.close()
            return response
        elif status_code == 404:
            response_body, content_len = self.create_html_template_error(status_code)
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                + "Content-Type: "
                + "text/html"
                + "\r\n"
                + "Referrer-Policy: "
                + "no-referrer\r\n"
                + "Content-Length: "
                + content_len
                + "\r\n"
                + "Connection: close"
                + "\r\n\r\n"
                + response_body
            )
            return response
        elif status_code == 405:
            response_body, content_len = self.create_html_template_error(status_code)
            response = (
                "HTTP/1.1 405 Method Not Allowed\r\n"
                + "Allow: GET\r\n"
                + ""
                + "Content-Type: "
                + "text/html"
                + "Content-Length: "
                + content_len
                + "\r\n"
                + "Connection: close"
                + "\r\n\r\n"
                + response_body
            )
            return response
        elif status_code == 301:
            f = open(file_path + "index.html", "r")
            response_body = f.read()
            response = (
                "HTTP/1.1 301 Moved Permanently\r\n"
                + "\r\n"
                + "Location: "
                + file_path
                + "index.html"
                + "\r\n"
                + "Content-Type: "
                + file_type
                + "\r\n"
                + "Content-Length: "
                + str(len(response_body))
                + "\r\n"
                + "Connection: keep-alive\r\n\r\n"
                + response_body
            )
            f.close()
            return response

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        decoded_data = self.data.decode("utf-8")

        split_data = decoded_data.split()

        request_method = split_data[0]
        request_path = split_data[1]
        prefix = "www"
        file_type = ""

        # Update file type for header
        if ".html" in request_path:
            file_type = "text/html"
        elif ".css" in request_path:
            file_type = "text/css"

        # Check if request is a GET request
        if request_method == "GET":
            path = prefix + request_path
            directory_traversal = "/../" in request_path
            # Validate path
            start_char = request_path[0]
            end_char = request_path[-1]
            valid_path = start_char == "/" and end_char == "/"

            if valid_path and not directory_traversal:
                # Check if path is a directory
                if os.path.isdir(path):
                    # Create file path to serve the 'index.html' file within the specified address
                    file_path = prefix + request_path + "index.html"
                    # Check if the 'file_path' reffered "in"file exists
                    if os.path.isfile(file_path):
                        # Create 200 OK response
                        response = self.create_response(file_path, "text/html", 200)
                        # Send response
                        self.request.sendall(bytearray(response, "utf-8"))
                # Path is a file
                else:
                    file_path = prefix + "/index.html"
                    response = self.create_response(file_path, "text/html", 200)
                    self.request.sendall(bytearray(response, "utf-8"))

            elif os.path.exists(path) and not directory_traversal:
                if os.path.isfile(path):
                    # Serve the file at "path" with the specified 'file_type'
                    response = self.create_response(path, file_type, 200)
                    self.request.sendall(bytearray(response, "utf-8"))

                elif os.path.isdir(path + "/"):
                    redirect_path = path + "/"

                    # Create 301 Moved Permanently response and redirect

                    response = self.create_response(redirect_path, file_type, 301)
                    self.request.sendall(bytearray(response, "utf-8"))
            # Handle directory traversal attempts and invalid paths
            else:
                response = self.create_response(None, file_type, 404)
                self.request.sendall(bytearray(response, "utf-8"))
        # Handle non-GET requests
        else:
            response = self.create_response(None, None, 405)
            self.request.sendall(bytearray(response, "utf-8"))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
