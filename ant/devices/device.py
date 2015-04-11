# Ant
#
# Copyright (c) 2012, Gustav Tiger <gustav@tiger.name>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os.path
import threading
import yaml

from ant.easy.channel import Channel
from ant.base.message import Message

class Device:
    def __init__(self, defaults):

        if defaults.has_key('name'):
            self.name = defaults['name']
            del defaults['name']
        else:
            self.name = False

        if defaults.has_key('config_file'):
            self.config_file = defaults['config_file']
            del defaults['config_file']
        else:
            self.config_file = False

        self.config = {
            'period': 8080,
            'search_timeout': 255,
            'rf_freq': 57,
            'device_id': 0,
            'device_type': 0,
            'transmission_type': 0,
        }

        self.config.update(defaults)

        if self.config_file and os.path.isfile(self.config_file) and self.name:
            config_file = open(self.config_file, 'r')
            config_content = yaml.safe_load(config_file)

            if config_content.has_key(self.name):
                self.config.update(config_content[self.name])

            config_file.close()

    def setup_channel(self, node):
        self.channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

        if not self._has_all_device_configurations():
            self.request_device_information()

        self.channel.on_broadcast_data = self.on_data
        self.channel.on_burst_data = self.on_data

        self.channel.set_period(self.config['period'])
        self.channel.set_search_timeout(self.config['search_timeout'])
        self.channel.set_rf_freq(self.config['rf_freq'])
        self.channel.set_id(self.config['device_id'], self.config['device_type'], self.config['transmission_type'])

        return self.channel

    def on_data(self, data):
        pass

    def request_device_information(self):
        while not self._has_all_device_configurations():
            channel, event, data = self.channel.request_message(Message.ID.RESPONSE_CHANNEL_ID)
            self.config['device_id'] = data[1] * 256 + data[0]
            self.config['device_type'] = data[2]
            self.config['transmission_type'] = data[3]

        if self.config_file and self.name:
            old_data = {}
            if os.path.isfile(self.config_file):
                config_file = open(self.config_file, 'r')
                old_data.update(yaml.safe_load(config_file)['self.name'])
                config_file.close()
            old_data[self.name] = self.config

            config_file = open(self.config_file, 'w')
            yaml.dump(old_data, config_file, default_flow_style = False)
            config_file.close()

    def _has_all_device_configurations(self):
        if self.config['device_id'] == 0 or self.config['device_type'] == 0 or self.config['transmission_type'] == 0:
            return False
        else:
            return True
