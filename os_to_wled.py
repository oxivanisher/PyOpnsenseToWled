#!/usr/bin/env python3

import json
import logging
import requests
import os
import yaml
import time

# Disable SSL error message
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)

class OpnsenseToWled:

    def __init__(self):
        self.config = {}
        self.last_config_reload = 0
        self.report_counter = 0
        self.update_rate = 1
        self.loss_data = []

    def get_opnsense_data(self):
        r = requests.get(self.config['opnsense']['url'],
                         auth=(self.config['opnsense']['api_key'], self.config['opnsense']['api_secret']),
                         verify=False)

        if r.status_code == 200:
            response = json.loads(r.text)

            if response['status'] == 'ok':
                for item in response['items']:
                    if item['name'] == self.config['opnsense']['gateway_name']:
                        self.loss_data.insert(0, float(item['loss'].replace(" %", "")))

            if len(self.loss_data) > 3600:
                self.loss_data = self.loss_data.insert[:3600]

        else:
            logging.error('Connection / Authentication issue, response received: %s' % r.text)

    def show_current_data(self):
        if self.report_counter > 20:
            for i in range(0, 20):
                logging.info("Now -%2s seconds: %5.2f %%" % (i, self.loss_data[i]))

            self.report_counter = 0
        else:
            self.report_counter += 1


    def load_config(self):
        if self.last_config_reload + 120 < time.time():
            config_file = os.path.join("config", "config.yml")
            with open(config_file) as file:
                logging.debug("Server loading config from %s" % config_file)
                self.config = yaml.load(file, Loader=yaml.FullLoader)
                self.last_config_reload = time.time()
                self.update_rate = self.config['ostowled']['update_rate']

    def run(self):
        logging.info("Opnsense to WLED starting")
        while True:
            self.load_config()
            self.get_opnsense_data()
            self.show_current_data()
            time.sleep(self.update_rate)

if __name__ == '__main__':
    ws_to_wled = OpnsenseToWled()
    ws_to_wled.run()
