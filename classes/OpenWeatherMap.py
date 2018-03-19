import httplib
import logging
import json


class OpenWeather:
    def __init__(self, config):
        self.config = config
        self.__weather_req = '/data/2.5/weather?q='
        self.__def_metric = '&units=metric'

    def get_tempo(self):
        resp = None
        try:
            conn = httplib.HTTPConnection(self.config['open_weather_api_link'])
            conn.request("GET", self.__weather_req
                         + self.config['default_city']
                         + self.__def_metric
                         + '&appid=' + self.config['owm_key'])
            req = conn.getresponse()
            if req.status == 200:
                resp = self._parse_response(resp=req.read())
        except Exception as e:
            logging.debug(e.message)
        finally:
            return resp

    def _parse_response(self, resp):
        data = None
        try:
            temp = json.loads(resp)
            data = {
                'temp': str(temp['main']['temp']),
                'pressure': str(temp['main']['pressure']),
                'humidity': str(temp['main']['humidity']),
                'weather_descr': temp['weather'][0]['description']
            }
        except Exception as e:
            logging.debug(e.message)
        return data
