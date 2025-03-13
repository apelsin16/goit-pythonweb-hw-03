import logging
import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO)


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key.strip(): value.strip() for key, value in [el.split('=') for el in data_parse.split('&')]}
        file_path = 'storage/data.json'
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_data = {
            timestamp: data_dict
        }
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if not isinstance(data, dict):
                    data = {}
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data.update(new_data)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        logging.info("Message added")
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('templates/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('templates/message.html')
        elif pr_url.path == '/read':
            self.send_json_to_html('templates/read.html')
        elif pr_url.path.startswith('/static/'):
            self.send_static()
        else:
            self.send_html_file('templates/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        file_path = pathlib.Path(self.path.lstrip("/"))
        self.send_response(200)
        mt = mimetypes.guess_type(file_path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())

    def send_json_to_html(self, filename):
        file_path = 'storage/data.json'

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('read.html')
        html_content = template.render(data=data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
