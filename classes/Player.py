import json
import vlc


class Player:
    _list = {}
    _stations = []
    _current_station = ''
    _previous_station = ''
    _current_station_indx = ''
    _current_station_link = {}

    _player_instance = None
    _vlc_instance = None

    is_playing = False
    stations_list = None

    def __init__(self):
        with open('stations.json') as json_data_file:
            self._list = json.load(json_data_file)
        self._stations = sorted(self._list)
        self.stations_list = self._stations[:]
        self._current_station_indx = 0

        self._init_player()
        self._load_station()

    def _init_player(self):
        self._vlc_instance = vlc.Instance()
        self._player_instance = self._vlc_instance.media_player_new()

    def _get_media_from_link(self, link):
        return self._vlc_instance.media_new(link)

    def prev_station(self):
        if self._current_station_indx == 0:
            self._current_station_indx = len(self._stations) - 1
        else:
            self._current_station_indx = self._current_station_indx - 1

        self._load_station()
        self.play()

    def next_station(self):
        if self._current_station_indx == len(self._stations) - 1:
            self._current_station_indx = 0
        else:
            self._current_station_indx = self._current_station_indx + 1

        self._load_station()
        self.play()

    def _load_station(self):
        self._previous_station = self._current_station
        self._current_station = self._stations[self._current_station_indx]
        self._current_station_link = self._list[self._current_station]['link']
        self._player_instance.set_media(
            self._get_media_from_link(
                self._current_station_link)
        )

    def set_station(self, station_name):
        for i in range(0, len(self._stations)):
            if self._stations[i] == station_name:
                self._current_station_indx = i
                self._load_station()

    def play(self):
        self._player_instance.play()
        self.is_playing = True

    def pause(self):
        self._player_instance.pause()
        self.is_playing = False

    def get_current_station(self):
        return self._current_station

    def get_previous_station(self):
        return self._previous_station
