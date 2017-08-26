from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import threading

import base64
import ssl

media_center_instance = None
config_instance = None
logger_instance = None
key = None


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        global config_instance, media_center_instance, key
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        key = base64.b64encode(config_instance['server_user_name'] + ':' + config_instance['server_user_password'])

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        global key
        if self.headers.getheader('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('{status: No auth received}')
        elif self.headers.getheader('Authorization') == 'Basic ' + key:
            self._set_headers()
            self.wfile.write("{status: success}")
        else:
            self.do_AUTHHEAD()
            self.wfile.write('{status: Not authenticated}')

    def do_HEAD(self):
        self._set_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Secure HTTP Environment\"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

    def parse_command_request(self):
        pass

    def parse_start(self):
        pass

    def parse_stop(self):
        pass


class SimpleServer(ThreadingMixIn, HTTPServer):
    """Handle request in new thread"""


class RequestServer:
    port = 10000
    server_address = ''
    httpd_thread = None
    httpd = None

    def __init__(self, utils, mc, logger):
        global logger_instance, media_center_instance, config_instance
        config_instance = utils.config
        media_center_instance = mc
        logger_instance = logger

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

