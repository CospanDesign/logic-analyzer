#! /usr/bin/env python

# Copyright (c) 2016 Dave McCoy (dave.mccoy@cospandesign.com)
#
# NAME is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NAME is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAME; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import logging
import argparse
import json
import select

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from device import device as dvc
from config import config as cfg
from sink import sink as sk

from device.uart.uart import UART
from config.config_file.config_file import ConfigFile
from sink.vcd.vcd import VCD

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "Logic Analyzer\n"

EPILOG = "\n" \
         "\t            CONTROL ----\n" \
         "\t               ^        |\n" \
         "\t               |        |\n" \
         "\t               V        V\n" \
         "\t[Signals] - DEVICE -> SINK -> [View/File]\n" \
         "\n"

DEVICES = [
    UART
]

CONFIGS = [
    ConfigFile
]

SINKS = [
    VCD
]


class LogicAnalyzer(object):

    def __init__(self, lax_config, debug = False):
        self.setup_logger()
        if debug:
            self.log.setLevel(logging.DEBUG)
        
        self.alive = True

        self.device = None
        self.config = None
        self.sink = None
        for dev in DEVICES:
            if dev.get_name() == lax_config["device"]:
                self.log.debug("Opening device: %s" % dev.get_name())
                self.open_device(dev, lax_config["device_path"])
                break

        for cg in CONFIGS:
            if cg.get_name() == lax_config["controller"]:
                self.log.debug("Opening device: %s" % cg.get_name())
                self.open_config(cg, lax_config["controller_path"])
                break

        for sk in SINKS:
            if sk.get_name() == lax_config["sink"]:
                self.log.debug("Opening device: %s" % sk.get_name())
                self.open_sink(sk, lax_config["sink_path"])
                break

    def setup_logger(self):
        self.log = logging.getLogger('LAX')
        #self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(filename)s:%(module)s:%(funcName)s: %(message)s')
        #formatter = logging.Formatter('%(pathname)s:%(module)s:%(funcName)s: %(message)s')

        #Create a Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        self.log.addHandler(ch)

    def open_device(self, device, path):
        self.log.debug("Openning Device: %s with path: %s" % (device.get_name(), path))
        self.device = device(path)
        self.device.set_callback(dvc.CALLBACK_CAPTURE, self.captured)

    def open_config(self, config, path):
        self.log.debug("Openning Config: %s with path: %s" % (config.get_name(), path))
        self.config = config(path)
        self.config.set_callback(cfg.CALLBACK_START, self.start_lax)
        self.config.set_callback(cfg.CALLBACK_STOP, self.stop_lax)
        self.config.set_callback(cfg.CALLBACK_FORCE, self.force_trigger)
        self.config.set_callback(cfg.CALLBACK_UPDATE, self.update_values)
        self.config.set_callback(cfg.CALLBACK_GET_SIZE, self.get_size)
        self.config.set_callback(cfg.CALLBACK_CLOSE, self.close)

    def open_sink(self, sink, path):
        self.log.debug("Openning Sink: %s with path: %s" % (sink.get_name(), path))
        self.sink = sink(path)

    def start_lax(self):
        self.log.debug("In Start LAX")
        self.sink.set_value(sk.ENABLE, True)
        self.log.debug("Starting the device")
        #XXX: This should launch a background thread!
        self.device.start()
        self.log.debug("Wait for data...")
        self.device.get_data()

    def stop_lax(self):
        self.device.stop()
        self.sink.set_value(sk.ENABLE, False)

    def force_trigger(self):
        self.device.force_trigger()
        self.device.get_data()

    def update_values(self):
        caps = self.device.get_capabilities()
        self.log.debug("Capabilities: %s" % str(caps))
        for cap in self.config.get_capabilities():
            self.log.debug("\tSetting capability: %s to %s" % (cap, str(self.config.get_value(cap))))
            try:
                self.device.set_value(cap, self.config.get_value(cap))
            except AssertionError as e:
                self.log.error("Device does not support: %s" % cap)

    def get_size(self):
        self.sink.set_value(sk.SIZE, self.device.get_size())

    def close_lax(self):
        self.alive = False

    def capture(self):
        self.log.info("Capture Detected!")
        self.config.captured()

    def ready(self):
        self.config.ready()

    def run(self):
        self.ready()
        '''
        inputs = [sys.stdin]
        outputs = []
        running = True

        while running:
            readible, writeable, execptional = select.select(inputs, outputs, inputs, timeout = 1)
            for s in readible:
                if s == sys.stdin:
                    data = sys.stdin.readline()
                    if data == "q":
                        running = False
                if s == 
        '''

    def close(self):
        self.running = False

    def captured(self, data):
        channel_dict = self.config.get_channel_dict()
        self.sink.generate_output(data, channel_dict)

def print_options():
    print "Devices/Config/Sink:"
    print ""
    print "Devices"
    for dev in DEVICES:
        print "\t%s" % dev.get_name()
    print "Controllers"
    for cg in CONFIGS:
        print "\t%s" % cg.get_name()
    print "Sinks"
    for snk in SINKS:
        print "\t%s" % snk.get_name()
    print ""

DEFAULT_CONFIG_FILE = "logic_config.json"

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("config",
                        nargs="?",
                        default=DEFAULT_CONFIG_FILE,
                        help="Configuration File: %s" % DEFAULT_CONFIG_FILE)

    parser.add_argument("-l", "--list",
                        action="store_true",
                        help="Enable Debug Messages")

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    if args.list:
        print_options()
        sys.exit(0)

    f = open(args.config, 'r')
    lax_config = json.loads(f.read())

    print "Arg Config: %s" % str(args.config)
    lax = LogicAnalyzer(lax_config, debug = args.debug)
    lax.run()
    '''if args.debug:
        print "test: %s" % str(args.test[0])
    '''

if __name__ == "__main__":
    main(sys.argv)


