import subprocess
import time


class Utils:
    temp_sensor_file = ''

    def __init__(self, sensor_file):
        self.temp_sensor_file = sensor_file

    @staticmethod
    def get_ram_usage():
        p1 = subprocess.Popen(["free"], stdout=subprocess.PIPE)
        p = subprocess.Popen(["awk", r'/Mem/{printf("%.2f \n"), $3/$2*100}'],
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
        result = "%.2f" % (tempo * 100 / (tempo + int(l[13]) - int(l[3])))
        return result

    @staticmethod
    def get_cpu_temp():
        p = subprocess.Popen(["cat", '/sys/devices/virtual/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE)
        time.sleep(0.1)
        line = p.stdout.readline()
        if line != '':
            return line.rstrip()
        else:
            return False

    def read_temp_raw(self):
        f = open(self.temp_sensor_file, 'r')
        str = f.readlines()
        f.close()
        return str

    def read_temp(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output + 2:]
            temp_c = str(round(float(temp_string) / 1000.0, 2))
            return temp_c
