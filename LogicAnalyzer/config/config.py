import logging
import json


TRIGGER             = "trigger"
TRIGGER_MASK        = "trigger_mask"
TRIGGER_EDGE        = "trigger_edge"
TRIGGER_BOTH_EDGE   = "both_edges"
TRIGGER_REPEAT      = "repeat"
TRIGGER_AFTER       = "trigger_after"

CAPABILITY_NAMES = [
TRIGGER,
TRIGGER_MASK,
TRIGGER_EDGE,
TRIGGER_BOTH_EDGE,
TRIGGER_REPEAT,
TRIGGER_AFTER
]


CALLBACK_START      = "start"
CALLBACK_STOP       = "stop"
CALLBACK_FORCE      = "force"
CALLBACK_UPDATE     = "update"
CALLBACK_GET_SIZE   = "get_size"
CALLBACK_CLOSE      = "close"


CALLBACK_NAMES = [
CALLBACK_START,
CALLBACK_STOP,
CALLBACK_FORCE,
CALLBACK_UPDATE,
CALLBACK_GET_SIZE,
CALLBACK_CLOSE
]

class Config(object):

    @staticmethod
    def get_name():
        return "Invalid Config, make your own!!"

    def __init__(self):
        self.log = logging.getLogger("LAX")
        self.caps = {}
        self.callbacks = {}
        self.channels = []
        for name in CAPABILITY_NAMES:
            self.caps[name] = None

        for name in CALLBACK_NAMES:
            self.callbacks[name] = None

    def get_channel_dict(self):
        """
        Return a dictionary that maps names to channel(s)
        """
        return self.channels

    def get_capabilities(self):
        """
        Return a list of capabilities (strings) that this device supports
        """
        names = []
        for name in self.caps:
            if self.caps[name] is not None:
                names.append(name)
        return names

    def has_capability(self, name):
        """
        Return true if the device has the capabilities
        """
        return self.caps[name] is not None

    def get_value(self, name):
        "Get the value of a capability"
        if not self.has_capability(name):
            raise AssertionError("LAX Does not have capability")
        else:
            return self.caps[name]

    def set_callback(self, name, func):
        self.log.debug("Setting callback for: %s" % name)
        self.callbacks[name] = func

    def ready(self):
        """The controller tells the config interface it's ready"""
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def captured(self):
        """callback when capture occurs"""
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)
