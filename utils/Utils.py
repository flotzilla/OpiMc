import subprocess
import time
import os.path

import yaml


class Utils:
    temp_sensor_file = ''
    config = {}
    logger = None
    _config_file = 'config.yaml'

    def __init__(self, logger):
        self.logger = logger

        self.config = self.read_config()
        self.temp_sensor_file = self.config['temp_sensor_file']

    def read_config(self):
        with open(self._config_file, 'r') as f:
            try:
                self.config = yaml.load(f)
                return self.config
            except yaml.YAMLError as exc:
                self.logger.error(exc.message)

    def save_config_to_file(self):
        with open(self._config_file, 'w') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False)

    def set_config_param(self, param_name, param_value):
        self.config[param_name] = param_value

    def get_cpu_temp(self):
        p = subprocess.Popen(["cat", self.config['cpu_temp_file']], stdout=subprocess.PIPE)
        time.sleep(0.1)
        line = p.stdout.readline()
        if line != '':
            return line.rstrip()
        else:
            return False

    def set_volume(self, volume_level):
        p = subprocess.Popen(['amixer sset "' + self.config['audio_device_name'] + '" ' + volume_level + '%'], stdout=subprocess.PIPE, shell=True)
        time.sleep(0.1)
        p.communicate()
        return True

    @staticmethod
    def get_ram_usage():
        p1 = subprocess.Popen(["free"], stdout=subprocess.PIPE)
        p = subprocess.Popen(["awk", r'/Mem/{printf("%.1f \n"), $3/$2*100}'],
                             stdout=subprocess.PIPE, stdin=p1.stdout)
        free_ram, err = p.communicate()
        return free_ram

    @staticmethod
    def get_cpu_load():
        p = subprocess.Popen(["grep", "cpu ", '/proc/stat'], stdout=subprocess.PIPE)
        time.sleep(0.5)
        p1 = subprocess.Popen(["grep", "cpu ", '/proc/stat'], stdout=subprocess.PIPE)

        stime, err = p.communicate()
        stime1, err = p1.communicate()

        # list
        l = (stime + stime1).replace("cpu  ", "").replace("\n", " ").split()

        tempo = int(l[10]) - int(l[0]) + int(l[12]) - int(l[2])
        result = "%.1f" % (tempo * 100 / (tempo + int(l[13]) - int(l[3])))
        return result

    def read_temp_raw(self):
        #if os.path.isfile(self.temp_sensor_file) is not True:
        return False
        #f = open(self.temp_sensor_file, 'r')
        #str = f.readlines()
        #f.close()
        #return str

    def read_temp(self):
        lines = self.read_temp_raw()
        if lines == False:
            return False
        counter = 1
        while lines[0].strip()[-3:] != 'YES' or counter == 5:
            time.sleep(0.1)
            lines = self.read_temp_raw()
            counter += 1
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output + 2:]
            temp_c = str(round(float(temp_string) / 1000.0, 2))
            return temp_c
        else:
            return False
