from http.server import BaseHTTPRequestHandler
import requests
import urllib3

target = 'localhost'

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    

    def do_proxy_requests(self):
        url = f"http://{target}{self.path}"
        req_headers = self.parse_headers()
        print("header read")
        req_body = self.read_body()
        print ("body read")

        req_headers['Host'] = target

        resp = requests.request(
            method=self.command,
            url=url,
            headers=req_headers,
            data=req_body,
            stream=True,
            allow_redirects=False)
        print("req done")

        self.send_response(resp.status_code)
        print("status_set")
        self.send_resp_headers(resp.headers)
        print("header sent")
        self.send_body_requests(resp)
        print ("body sent")

    def do_proxy_urllib3(self):
        url = f"http://{target}{self.path}"
        req_headers = self.parse_headers()
        print("header read")
        req_body = self.read_body()
        print ("body read")

        req_headers['Host'] = target

        print("Connecting", url)
        resp = urllib3.request(
            self.command,
            url,
            headers=req_headers,
            body=req_body,
            preload_content=False,
            redirect=True)

        print("req done")

        self.send_response(resp.status)
        print("status_set")
        self.send_resp_headers(resp.headers)
        print("header sent")
        self.send_body_urllib3(resp)
        print ("body sent")

    do_proxy = do_proxy_urllib3

    do_HEAD = do_proxy
    do_GET = do_proxy
    do_POST = do_proxy
    do_PUT = do_proxy
    do_PATCH = do_proxy
    do_DELETE = do_proxy
    do_OPTIONS = do_proxy
    do_TRACE = do_proxy

    def parse_headers(self):
        headers = dict()
        for key in self.headers:
            headers[key] = self.headers[key]
        return headers
    
    def send_resp_headers(self, headers):
        for key in headers:
            self.send_header(key, headers[key])
        self.end_headers()

    def send_body_requests(self, resp):
        if resp.headers.get('Transfer-Encoding') != 'chunked':
            print("not chunked")
            size = 0
            while True:
                chunk = resp.raw.read(128, False)
                if not chunk:
                    break
                size += len(chunk)
                self.wfile.write(chunk)
            print("size was:", size)
            if size == 0 and resp.headers.get("Content-Length") != 0:
                print("Fixed response body with content value")
                self.wfile.write(resp.content)
        else:
            print ("chunked")
            for chunk in resp.raw.read_chunked(128, False):
                self.wfile.write(bytes(f"{len(chunk):x}", 'utf-8') + b"\r\n")
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
            
            self.wfile.write(b"0\r\n")
            self.wfile.write(b"\r\n")

    def send_body_urllib3(self, resp):
        chunked = resp.headers.get('Transfer-Encoding') == 'chunked'
        for chunk in resp.stream(128):
            if chunked:
                self.wfile.write(bytes(f"{len(chunk):x}", 'utf-8') + b"\r\n")
            self.wfile.write(chunk)
            if chunked:
                self.wfile.write(b"\r\n")

        if chunked:
            self.wfile.write(b"0\r\n")
            self.wfile.write(b"\r\n")

    def read_body(self):
        content_len = int(self.headers.get('content-length', 0))
        return self.rfile.read(content_len)