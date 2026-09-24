import http.server
import socketserver
import os
import sys
import webbrowser
import json

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class AerisHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            status = {
                "status": "online",
                "system": "AERIS Environmental Intelligence Platform",
                "version": "DeepDispersion v4.2.1",
                "data_source": "india_forecast.csv & region_forecast.csv"
            }
            self.wfile.write(json.dumps(status).encode('utf-8'))
            return
        elif self.path == '/api/data':
            json_file = os.path.join(DIRECTORY, 'data', 'forecastData.json')
            if os.path.exists(json_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(json_file, 'rb') as f:
                    self.wfile.write(f.read())
                return
        return super().do_GET()

def start_server():
    global PORT
    while PORT < 3020:
        try:
            with socketserver.TCPServer(("", PORT), AerisHandler) as httpd:
                url = f"http://localhost:{PORT}"
                print("=" * 65)
                print(" AERIS // Environmental Intelligence Platform")
                print(f" Server running at: {url}")
                print(f" Serving directory: {DIRECTORY}")
                print(" Press Ctrl+C to stop the server.")
                print("=" * 65)
                webbrowser.open(url)
                httpd.serve_forever()
        except OSError:
            PORT += 1

if __name__ == '__main__':
    start_server()
