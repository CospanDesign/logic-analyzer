import logging

TRIGGER             = "trigger"
TRIGGER_MASK        = "trigger mask"
TRIGGER_EDGE        = "trigger edge"
TRIGGER_BOTH_EDGE   = "both edges"
TRIGGER_REPEAT      = "repeat"
TRIGGER_AFTER       = "trigger after"
FORCE_TRIGGER       = "force trigger"
SIZE                = "size"
ENABLE              = "enable"

VIEW_NAMES = [
TRIGGER,
TRIGGER_MASK,
TRIGGER_EDGE,
TRIGGER_BOTH_EDGE,
TRIGGER_REPEAT,
TRIGGER_AFTER,
FORCE_TRIGGER,
SIZE,
ENABLE
]



class Sink(object):

    @staticmethod
    def get_name():
        return "Invalid Name!"

    def __init__(self):
        self.log = logging.getLogger("LAX")

    def generate_output(self, data, channel_dict):
        pass

    def update_output(self, data, channel_dict):
        """ Append the generated output data"""
        pass
            
    def set_value(name, value):
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)
