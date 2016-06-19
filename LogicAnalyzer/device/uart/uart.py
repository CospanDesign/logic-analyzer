import logging
import sys
import os
import argparse
from array import array as Array

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from device.device import *
from device.device import Device


class UART(Device):

    @staticmethod
    def get_name():
        return "uart"

    def __init__(self, path):
        Device.__init__(self)
        self.caps[TRIGGER]
        self.log = logging.getlogger("lax")
        self.dev = None
        self.open(path)

    def open(self, path):
        self.log.info("Openning")
        self.dev = 

    def set_trigger(self, value):
        pass

    def set_trigger_mask(self, value):
        pass

    def set_trigger_edge(self, value):
        pass

    def set_trigger_both_edges(self, value):
        pass

    def set_trigger_repeat(self, value):
        pass

    def set_trigger_after(self, value):
        pass

    def start(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def stop(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def force_trigger(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)
