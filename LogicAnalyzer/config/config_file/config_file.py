import logging
import json
import sys
import os
from array import array as Array


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from config.config import *

#JSON keys:
CHANNELS = "channels"
CONFIG = "config"

class ConfigFile(Config):

    @staticmethod
    def get_name():
        return "file"

    def __init__(self, path):
        Config.__init__(self)
        f = open(path, 'r')
        self.config = json.loads(f.read())
        f.close()
        print "Config: %s" % str(self.config[CONFIG])

        for c in CAPABILITY_NAMES:
            if c in self.config[CONFIG].keys():
                self.caps[c]  = int(self.config[CONFIG][c], 16)

        self.channels = self.config[CHANNELS]

    def ready(self):
        self.log.debug("Configure the logic analzyer")
        #Configure the logic analyzer
        if self.callbacks[CALLBACK_UPDATE] is not None:
            self.callbacks[CALLBACK_UPDATE]()
        self.log.debug("Start the logic analyzer")
        #Start the logic analyzer
        #self.callbacks[CALLBACK_FORCE]()
        if self.callbacks[CALLBACK_START] is not None:
            self.log.debug("Start LAX exists")
            self.callbacks[CALLBACK_START]()

    def captured(self):
        if self.callbacks[CALLBACK_CLOSE] is not None:
            self.callbacks[CALLBACK_CLOSE]()
