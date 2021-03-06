import logging

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


CALLBACK_CAPTURE    = "close"

CALLBACK_NAMES = [
CALLBACK_CAPTURE
]

class Device(object):

    @staticmethod
    def get_name():
        "Invalid! Overide this method!"

    def __init__(self):
        self.log = logging.getLogger("LAX")
        self.caps = {}
        self.callbacks = {}
        for name in CAPABILITY_NAMES:
            self.caps[name] = None

        for name in CALLBACK_NAMES:
            self.callbacks[name] = None

        #Set this to tell the user what capabilities are available
        #Replace all the 'None' with functions that will accept the variables

        #Example Setting trigger to a function:
        #self.caps[TRIGGER]           = self.set_trigger
        #Example Setting trigger mask to a function:
        #self.caps[TRIGGER_MASK]      = self.set_trigger_mask

        #Open Your Device HERE

    def get_size(self):
        """
        return the size of your capture window
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

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

    def set_value(self, name, value):
        "Set the value of the logic analyzer"
        if not self.has_capability(name):
            raise AssertionError("LAX Does not have capability")
        else:
            self.caps[name](value)

    def reset(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def start(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def stop(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def force_trigger(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def get_num_channels(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def get_channel_names(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def get_data(self):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def set_callback(self, name, func):
        self.callbacks[name] = func

