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

from mock import Mock
import unittest
import shutil
import tempfile
import yaml

from ant.devices.device import Device

class DeviceRequestDeviceInformationTest(unittest.TestCase):
    def runTest(self):
        device = Device({})
        device.channel = Mock()
        device.channel.request_message = Mock(side_effect = [[0, 1, [1, 0, 2, 3]]])

        device.request_device_information()

        self.assertEquals(device.config['device_id'], 1)
        self.assertEquals(device.config['device_type'], 2)
        self.assertEquals(device.config['transmission_type'], 3)

class DeviceRequestDeviceInformationFirstNullInformationTest(unittest.TestCase):
    def runTest(self):
        device = Device({})
        device.channel = Mock()
        device.channel.request_message = Mock(side_effect = [
            [0, 1, [0, 0, 0, 0]], [0, 1, [1, 0, 2, 3]]])

        device.request_device_information()

        self.assertEquals(device.config['device_id'], 1)
        self.assertEquals(device.config['device_type'], 2)
        self.assertEquals(device.config['transmission_type'], 3)

class DeviceLoadingDeviceIdFromFileTest(unittest.TestCase):
    def runTest(self):
        tmpdir = tempfile.mkdtemp()
        config_file = tmpdir + '/config.yml'
        f_cfg = open(config_file, 'w')
        yaml.dump( { 'device' : { 'device_id': 123 } }, f_cfg)
        f_cfg.close()

        device = Device({'name': 'device', 'config_file': config_file})

        self.assertEquals(device.config['device_id'], 123)

        shutil.rmtree(tmpdir)

class DeviceRequestDeviceInformationWritesConfigFileTest(unittest.TestCase):
    def runTest(self):
        tmpdir = tempfile.mkdtemp()
        config_file = tmpdir + '/config.yml'

        device = Device({'name': 'device', 'config_file': config_file})
        device.channel = Mock()
        device.channel.request_message = Mock(side_effect = [[0, 1, [1, 1, 2, 3]]])

        device.request_device_information()

        f_cfg = open(config_file, 'r')
        config_content = yaml.load(f_cfg)
        self.assertEquals(config_content['device']['device_id'], 257)
        f_cfg.close()

        shutil.rmtree(tmpdir)
