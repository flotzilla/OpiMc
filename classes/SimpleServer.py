import base64
import ssl
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

media_center_instance = None
config_instance = None
logger_instance = None


class RequestHandler(SimpleHTTPRequestHandler):
    key = None

    def __init__(self, request, client_address, server):
        global config_instance, media_center_instance
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
        self.key = base64.b64encode(config_instance['server_user_name'] + ':' + config_instance['server_user_password'])

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.headers.getheader('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('No auth received')
        elif self.headers.getheader('Authorization') == 'Basic ' + self.key:
            self._set_headers()
            self.wfile.write("<body><p>This is a test.</p>")
        else:
            self.do_AUTHHEAD()
            self.wfile.write('Not authenticated')

    def do_HEAD(self):
        self._set_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Secure HTTP Environment\"')
        self.send_header('Content-type', 'text/html')
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


class SimpleServer:
    def __init__(self, utils, mc, logger):
        global logger_instance, media_center_instance, config_instance
        config_instance = utils.config
        media_center_instance = mc
        logger_instance = logger

        self.server_address = utils.config['server_address']
        self.port = utils.config['server_port']

    def run(self):
        global config_instance
        server_address = (self.server_address, self.port)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.socket = ssl.wrap_socket(httpd.socket,
                                       certfile='./' + config_instance['ssl_cert_file_location'],
                                       server_side=True)
        httpd.serve_forever()
