from http.server import BaseHTTPRequestHandler
import requests

target = 'amazon.de'

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        url = f"http://{target}{self.path}"
        req_headers = self.parse_headers()
        req_headers['Host'] = target

        resp = requests.get(url, req_headers, stream=True)

        self.send_response(resp.status_code)
        self.send_resp_headers(resp)
        if body:
            self.send_body(resp)

    
    def parse_headers(self):
        headers = dict()
        for key in self.headers:
            headers[key] = self.headers[key]
        return headers
    
    def send_resp_headers(self, resp):
        if 'content-length' not in resp.headers and 'Content-Length' not in resp.headers:
            print(resp.headers)
        for key in resp.headers:
            self.send_header(key, resp.headers[key])
        self.end_headers()

    def send_body(self, resp):
        if 'content-length' in resp.headers:
            while True:
                chunk = resp.raw.read(128, False)
                if not chunk:
                    break
                self.wfile.write(chunk)
        else:
            for chunk in resp.raw.read_chunked(128, False):
                self.wfile.write(bytes(f"{len(chunk):x}", 'utf-8') + b"\r\n")
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
            
            self.wfile.write(b"0\r\n")
            self.wfile.write(b"\r\n")