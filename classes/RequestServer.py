from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import threading

import base64
import ssl

media_center_instance = None
config_instance = None
utils_instance = None
logger_instance = None
key = None


class RequestHandler(SimpleHTTPRequestHandler):
    json_content_type = 'application/json'
    server_version = 'Apachan-webservar/1337' # hide server credentials

    def __init__(self, request, client_address, server):
        global config_instance, media_center_instance, key
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        key = base64.b64encode(config_instance['server_user_name'] + ':' + config_instance['server_user_password'])

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', self.json_content_type)
        self.end_headers()

    def check_auth(self):
        global key, config_instance
        if key is None:
            key = base64.b64encode(config_instance['server_user_name'] + ':' + config_instance['server_user_password'])

        if self.headers.getheader('Authorization') is None:
            self.do_auth_head()
            self.wfile.write('{status: "No auth received"}')
            return False
        elif self.headers.getheader('Authorization') == 'Basic ' + key:
            self._set_headers()
            return True

    def do_auth_head(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Secure HTTP Environment\"')
        self.send_header('Content-type', self.json_content_type)
        self.end_headers()

    def do_GET(self):
        if self.check_auth():
            self.parse_command_request()
        else:
            self.do_auth_head()
            self.wfile.write('{status: "Not authenticated"}')

    def do_HEAD(self):
        if self.check_auth():
            self.wfile.write('{status: "ok", message: "method not supported"')
        else:
            self.do_auth_head()
            self.wfile.write('{status: "Not authenticated"}')

    def do_POST(self):
        if self.check_auth():
            self.wfile.write('{status: "ok", message: "method not supported"')
        else:
            self.do_auth_head()
            self.wfile.write('{status: "Not authenticated"}')

    def parse_command_request(self):
        request = urlparse(self.path)
        query = parse_qs(request.query)

        if request.path == '/get-current-station':
            self.parse_get_current_station(query)
        elif request.path == '/get-temp':
            self.parse_get_temp()
        else:
            self.wfile.write('{status: "ok"}')

    def parse_get_current_station(self, query):
        # test_param = query.get('test', None)
        # if test_param is not None:
        #     print test_param[0]
        self.wfile.write('{status: "ok"')

    def parse_get_temp(self):
        global utils_instance
        self.wfile.write('status: "ok", temperature: ' + utils_instance.read_temp() + '"')

    def version_string(self):
        return self.server_version


class SimpleServer(ThreadingMixIn, HTTPServer):
    """Handle request in new thread"""


class RequestServer:
    port = 10000
    server_address = ''
    httpd_thread = None
    httpd = None

    def __init__(self, utils, mc, logger):
        global logger_instance, media_center_instance, config_instance, utils_instance
        config_instance = utils.config
        media_center_instance = mc
        logger_instance = logger
        utils_instance = utils

        self.server_address = utils.config['server_address']
        self.port = utils.config['server_port']

    def run(self):
        global config_instance, logger_instance
        server_address = (self.server_address, self.port)
        self.httpd = SimpleServer(server_address, RequestHandler)
        self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
                                            certfile='./' + config_instance['ssl_cert_file_location'],
                                            server_side=True)
        self.httpd_thread = threading.Thread(target=self.httpd.serve_forever)
        self.httpd_thread.daemon = True
        logger_instance.debug('starting main thread')
        self.httpd_thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

