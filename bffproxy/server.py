import socketserver
from .handler import ProxyHTTPRequestHandler

def start_server():
    server_address = ('0.0.0.0', 8081)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, ProxyHTTPRequestHandler) as httpd:
        httpd.serve_forever()