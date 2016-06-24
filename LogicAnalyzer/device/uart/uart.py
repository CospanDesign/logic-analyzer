import sys
import os
import serial
from array import array as Array

import sys
import select
import tty
import termios

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


from device.device import *
from device.device import Device


NUM_CHANNELS        = 32    #XXX: For now this is a constant

BAUDRATE            = 115200


PING_CMD            = "W0\n"
RESET_CMD           = "W;\n"
ENABLE_CMD          = "W1%d\n"
IS_ENABLED_CMD      = "W2\n"
FORCE_TRIGGER_CMD   = "W<\n"
TRIGGER_CMD         = "W4%08X\n"
TRIGGER_MASK_CMD    = "W5%08X\n"
TRIGGER_AFTER_CMD   = "W6%08X\n"
TRIGGER_EDGE_CMD    = "W7%08X\n"
BOTH_EDGES_CMD      = "W8%08X\n"
REPEAT_COUNT_CMD    = "W9%08X\n"
GET_SIZE_CMD        = "W3\n"
GET_START_POS_CMD   = "W:\n"


class DeviceFinished(Exception):
    pass

class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False

def array_to_dword(a):
    return (a[0] << 24) | (a[1] << 16) | (a[2] << 8) | a[3]

class UART(Device):

    @staticmethod
    def get_name():
        return "uart"

    def __init__(self, path, debug = False):
        Device.__init__(self)
        self.caps[TRIGGER]          = self.set_trigger
        self.caps[TRIGGER_MASK]     = self.set_trigger_mask
        self.caps[TRIGGER_EDGE]     = self.set_trigger_edge
        self.caps[TRIGGER_BOTH_EDGE]= self.set_trigger_both_edges
        self.caps[TRIGGER_REPEAT]   = self.set_trigger_repeat
        self.caps[TRIGGER_AFTER]    = self.set_trigger_after

        self.dev = None
        self._open(str(path))

    def _open(self, path):
        self.log.info("Openning...")
        self.dev = serial.Serial(path, BAUDRATE, timeout = 2, stopbits=2)
        self.log.debug("flushing...")
        self.dev.write("\n\n\n\n\n\n\n\n\n\n")
        self.dev.flush()

        if self._ping():
            self.log.info("Opened")
        else:
            self.log.info("Failed to open")
        self.get_size()

    def _read_response(self):
        read_data = self.dev.readline()
        while "R" not in read_data:
            read_data = Array('B', self.dev.readline())

        return "R" + read_data.partition("R")[2]

    def _ping(self):
        self.dev.flush()
        self.dev.write(PING_CMD)
        self.log.debug("See if the device is there?")
        #data = Array('B', self.dev.read(4))
        data = Array('B', self._read_response())
        print "Data: %s" % str(data)
        if data.tostring()[1] == "S":
            self.log.debug("Ping Response Successful")
            return True
        else:
            self.log.debug("Ping Response Fail")
            return False

    def reset(self):
        self.dev.write(RESET_CMD)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger(self, value):
        d = TRIGGER_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger_mask(self, value):
        d = TRIGGER_MASK_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger_edge(self, value):
        d = TRIGGER_EDGE_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger_both_edges(self, value):
        d = BOTH_EDGES_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger_repeat(self, value):
        d = REPEAT_COUNT_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def set_trigger_after(self, value):
        d = TRIGGER_AFTER_CMD % value
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def start(self):
        d = ENABLE_CMD % 1
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def stop(self):
        d = ENABLE_CMD % 0
        self.log.debug("Data Out: %s" % d)
        self.dev.write(d)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def force_trigger(self):
        self.dev.write(FORCE_TRIGGER_CMD)
        #data = self.dev.read(4)
        data = self._read_response()
        self.log.debug("Data: %s" % data)

    def get_size(self):
        self.dev.write(GET_SIZE_CMD)
        #self.size = int(self.dev.read(12)[2:10], 0)
        size_str = self._read_response()[2:10]
        print "Size string: %s" % size_str
        self.size = int(size_str, 16)
        self.log.debug("Size: 0x%08X" % self.size)

    def get_num_channels(self):
        return NUM_CHANNELS

    def get_channel_names(self):
        names = []
        for i in range(NUM_CHANNELS):
            names.append("%s" % i)
        return names

    def get_data(self):
        self.log.debug("Wating for data...")
        length = 8 + 8 * self.size
        read_data = ""
        with NonBlockingConsole() as nbc:
            while len(read_data) < length:
                print "reading..."
                read_data += self.dev.read(length - len(read_data))
                if "R" in read_data:
                    print "Detected previous end transaction..."
                    read_data = read_data.partition("\n")[2]
                    print "read data: %s" % read_data
                    print "Length: %d" % len(read_data)

                key = nbc.get_data()
                if not key:
                    continue
                key = key.lower()[0]
                if key == 'f':
                    self.log.info("Force Capture")
                    #self.force_trigger()
                    self.set_trigger_mask(0x00)
                    self.start()
                if key == 'q':
                    raise DeviceFinished()

        data = Array('B', read_data.decode("hex"))
        l = len(data)
        print "Length of data: %d" % l
        print "Length of data: 0x%08X" % l
        #self.log.debug("Received: %d [0x%08X]peices of data" % (len(data), len(data)))
        start_pos = array_to_dword(data[0:4])
        data = data[4:]
        #Fix the data order
        temp = Array('L')
        for i in range (0, len(data), 4):
            temp.append(array_to_dword(data[i: i + 4]))

        data = Array('L')
        if start_pos == 0:
            data = temp

        data.extend(temp[start_pos:])
        data.extend(temp[0:start_pos])
        self.callbacks[CALLBACK_CAPTURE](data)
        return data

