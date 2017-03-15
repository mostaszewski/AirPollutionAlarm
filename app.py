"""
    The script is designed for monitoring the level of air pollution.
    Locates users on the basis of IP address, then gets data from the nearest monitoring
    station and sends a report to the provided e-mail address.
"""

import configparser
import logging
import time

import requests

from emailsender import EmailSender

logging.basicConfig(level=logging.INFO)

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
SCALE = {
    'pm10': {
        'Very good': [0, 21],
        'Good': [21, 61],
        'Moderate': [61, 101],
        'Sufficient': [101, 141],
        'Bad': [141, 201],
        'Very bad': [201, 10000],
    },
    'pm25': {
        'Very good': [0, 13],
        'Good': [13, 36],
        'Moderate': [36, 61],
        'Sufficient': [61, 84],
        'Bad': [84, 121],
        'Very bad': [121, 10000],
    }
}


class AirPollutionAlarm:
    continue_loop = False

    def __init__(self):
        logging.info("Air Pollution Alarm")

    @staticmethod
    def get_data():
        """
            Downloads information from the nearest monitoring station regarding the
            air pollution level.
        """
        response = requests.get('http://api.waqi.info/feed/here/?token={}'.format(
            CONFIG['API']['Token']))
        data = response.json()['data']

        station = data['city']['name']
        last_update = data['time']['s']
        pm10 = data['iaqi']['pm10']['v']
        pm25 = data['iaqi']['pm25']['v']

        pm10_level = [level for level, value in SCALE['pm10'].items() if
                      pm10 in range(value[0], value[1])][0]
        pm25_level = [level for level, value in SCALE['pm25'].items() if
                      pm25 in range(value[0], value[1])][0]

        result = {
            'station': station,
            'last_update': last_update,
            'pm10': pm10,
            'pm10_level': pm10_level,
            'pm25': pm25,
            'pm25_level': pm25_level
        }

        return result

    def run(self):
        """
            Monitors the air pollution level and sends a report to the provided
            e-mail address.
        """
        self.continue_loop = True
        while self.continue_loop:
            data = self.get_data()
            if not EmailSender(CONFIG, data).send_email():
                self.stop()
                break
            time.sleep(int(CONFIG['API']['Refresh rate']))

    def stop(self):
        self.continue_loop = False


if __name__ == "__main__":
    app = AirPollutionAlarm()
    app.run()
