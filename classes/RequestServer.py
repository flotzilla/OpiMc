from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import threading

import base64
import ssl
import json

media_center_instance = None
config_instance = None
utils_instance = None
logger_instance = None
key = None


class RequestHandler(SimpleHTTPRequestHandler):
    json_content_type = 'application/json'
    server_version = 'Apachan-webservar/1337'  # hide server credentials

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
        else:
            self.do_auth_head()
            self.wfile.write('{status: "Not authenticated"}')
            return False

    def do_auth_head(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Secure HTTP Environment\"')
        self.send_header('Content-type', self.json_content_type)
        self.end_headers()

    def do_GET(self):
        if self.check_auth():
            self.parse_command_request()

    def do_HEAD(self):
        if self.check_auth():
            response = json.dumps({
                'status': 'ok, but wait',
                'message': 'method not supported'
            })
            self.wfile.write(response)

    def do_POST(self):
        if self.check_auth():
            response = json.dumps({
                'status': 'ok, but wait',
                'message': 'method not supported'
            })
            self.wfile.write(response)

    def parse_command_request(self):
        request = urlparse(self.path)
        query = parse_qs(request.query)

        if request.path == '/player-get-state':
            self.parse_get_player_state(query)
        elif request.path == '/get-temp':
            self.parse_get_temp()
        elif request.path == '/player_play_stop':
            self.parse_player_play_stop()
        elif request.path == '/player_next':
            self.parse_player_next_station()
        elif request.path == '/player_previous':
            self.parse_player_previous_station()
        elif request.path == '/player_get_stations_list':
            self.parse_get_player_stations_list()
        elif request.path == '/set_volume':
            self.set_sound_level(query)
        else:
            self.wfile.write('{status: "ok"}')

    def parse_get_player_state(self, query):
        # test_param = query.get('test', None)
        # if test_param is not None:
        #     print test_param[0]
        global media_center_instance
        response = json.dumps({
            'status': 'ok',
            'current_station': media_center_instance.player.get_current_station(),
            'is_playing': media_center_instance.player.is_playing
        })
        self.wfile.write(response)

    def parse_get_temp(self):
        global utils_instance

        response = json.dumps({
            'status': 'ok',
            'temperature': utils_instance.read_temp()
        })
        self.wfile.write(response)

    def parse_player_play_stop(self):
        global media_center_instance
        message = 'Let there be rock'

        if media_center_instance.player.is_playing:
            message = 'Let there be silence'
            media_center_instance.player.pause()
        else:
            media_center_instance.player.play()

        response = json.dumps({
            'status': 'ok',
            'message': message
        })
        self.wfile.write(response)

    def parse_player_next_station(self):
        global media_center_instance
        media_center_instance.player.next_station()

        response = json.dumps({
            'status': 'playing next station',
            'current_station': media_center_instance.player.get_current_station()
        })
        self.wfile.write(response)

    def parse_player_previous_station(self):
        global media_center_instance
        media_center_instance.player.prev_station()

        response = json.dumps({
            'status': 'playing next station',
            'current_station': media_center_instance.player.get_current_station()
        })
        self.wfile.write(response)

    def parse_get_player_stations_list(self):
        response = json.dumps({
            'status': 'ok',
            'stations_list': media_center_instance.player.stations_list
        })
        self.wfile.write(response)

    def set_sound_level(self, get_params):
        if 'level' in get_params and get_params['level']:
            global utils_instance
            utils_instance.set_volume(get_params['level'][0])
            response = json.dumps({
                'status': 'ok',
                'sound_level': 'will be set to ' + get_params['level'][0]
            })
        else:
            response = json.dumps({
                'status': 'bad',
                'message': 'cannot get level param'
            })
        self.wfile.write(response)

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

