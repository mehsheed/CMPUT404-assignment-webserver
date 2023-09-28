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

    
    #TODO : Create a HTML_Template function that takes Response Code and generates standard HTML response for response function
    #TODO : Create a response function that takes in a file path, file type, and status code
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK",'utf-8'))
        decoded_data = self.data.decode("utf-8")
        split_data = decoded_data.split()
        request_method = split_data[0]
        request_path = split_data[1]
        prefix = "www"
        file_type = ""

        #Update file type for header
        if ".html" in request_path :

            file_type = "text/html"
        elif ".css" in request_path:
                
            file_type = "text/css"

        #Check if request is a GET request
        if request_method == "GET":
            
            directory_traversal = "/../" in request_path
            path = prefix + request_path
            #Validate path
            start_char = request_path[0]
            end_char = request_path[-1]
            valid_path = (start_char == "/" and end_char == "/")

            if not (directory_traversal) and valid_path:

                #Check if path is a directory
                if os.path.isdir():
                    #Create file path to serve the 'index.html' file within the specified address
                    file_path = prefix + request_path + "index.html"
                    #Check if the 'file_path' reffered "in"file exists
                    if os.path.isfile(file_path):
                        #Create 200 OK response
                        response = self.create_response(file_path, file_type,200)
                        #Send response
                        self.request.sendall(bytearray(response,'utf-8'))
                #Path is a file
                else:
                    file_path = prefix + "/index.html"
                    response = self.create_response(file_path, file_type,200)
                    self.request.sendall(bytearray(response,'utf-8'))
            elif (os.path.exists(path) and not directory_traversal):
                if os.path.isfile(path):
                    #Serve the file at "path" with the specified 'file_type'
                    response = self.create_response(path, file_type,200)
                    self.request.sendall(bytearray(response,'utf-8'))   

                






                
        






if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
