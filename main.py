from concurrent.futures import ThreadPoolExecutor

import json

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

import mimetypes
import os
from urllib.parse import unquote_plus, urlparse

from datetime import datetime
from time import sleep


class HTTPHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        url = urlparse(self.path)
        match url.path:
            case "/":
                self.send_html_file("index.html")
            case "/message":
                self.send_html_file("message.html")
            case _ if os.path.exists(url.path[1:]):
                self.send_static_file(url.path[1:])
            case _:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()
        print(raw_data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(raw_data, ("127.0.0.1", 5000))
        print(raw_data, 22222222)

    def send_html_file(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(filename, "rb") as file:
            data = file.read()
            self.wfile.write(data)

    def send_static_file(self, filename, status_code=200):
        mimetype = mimetypes.guess_type(filename)
        self.send_response(status_code)

        if mimetype:
            self.send_header('Content-type', mimetype[0])
        else:
            self.send_header('Content-type', "text/plain")
        
        self.end_headers()

        with open(filename, "rb") as file:
            data = file.read()
            self.wfile.write(data)


def run_http_server(ip, port):
    address = (ip, port)
    http = HTTPServer(address, HTTPHandler)

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_udp_server(ip, port):
    data = load_data()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    try:
        while True:
            raw_client_info, address = sock.recvfrom(1024)
            print(raw_client_info, 33333333333)
            client_info_parse = unquote_plus(raw_client_info.decode())
            client_info = {key: value for key, value in [x.split("=") for x in client_info_parse.split("&")]}
            data[str(datetime.now())] = client_info
            save_data(data)
            print(f'From client: {data}')
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def load_data():
    with open("storage/data.json", "r") as file:
        data = json.load(file)

    return data


def save_data(data):
    with open("storage/data.json", "w") as file:
        json.dump(data, file)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as thread:
        thread.submit(run_http_server, "127.0.0.1", 3000)
        thread.submit(run_udp_server, "127.0.0.1", 5000)


    print('sd')