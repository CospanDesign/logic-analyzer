import logging
import json
import sys
import os
import time
from collections import OrderedDict
from array import array as Array

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from sink.sink import *

class VCD(Sink):

    @staticmethod
    def get_name():
        return "vcd"

    def __init__(self, path):
        Sink.__init__(self)
        self.path = path
        self.trigger = 0x00
        self.trigger_mask = 0x00
        self.trigger_edge = 0x00
        self.both_edge = 0x00
        self.trigger_repeat = 0x00
        self.trigger_after = 0x00
        self.size = 0x00
        self.enable = False

    def generate_output(self, data, channel_dict):
        self.log.debug("Generate an output!")
        #XXX: Need a better way to express the width of data
        size = 32
        #if type(data[0]) is int:
        #    size = 32

        #signal_dict = OrderedDict(channel_dict)
        '''
        signal_dict = OrderedDict()
        for i in range(size):
            signal_dict["signal%d" % i] = 1
        '''

        buf = self.create_vcd_buffer(data, signal_dict = OrderedDict(), count = size, clock_count = 100, add_clock = True, debug = True)
        f = open(self.path, "w")
        f.write(buf)
        f.close()

    def update_output(self, data, size):
        pass

    def set_vcd_header(self):
        #set date
        buf = ""
        buf += "$date\n"
        buf += time.strftime("%b %d, %Y %H:%M:%S") + "\n"
        buf += "$end\n"
        buf += "\n"

        #set version
        buf += "$version\n"
        buf += "\tNysa Logic Analyzer V0.1\n"
        buf += "$end\n"
        buf += "\n"

        #set the timescale
        buf += "$timescale\n"
        buf += "\t1 ns\n"
        buf += "$end\n"
        buf += "\n"

        return buf

    def set_signal_names(self, signal_dict, add_clock):
        buf = ""

        #set the scope
        buf += "$scope\n"
        buf += "$module logic_analyzer\n"
        buf += "$end\n"
        buf += "\n"

        offset = 0
        char_offset = 33
        if add_clock:
            character_alias = char_offset
            buf += "$var wire 1 %c clk $end\n" % (character_alias)
            char_offset = 34

        offset = 0
        for name in signal_dict:
            try:
                character_alias = char_offset + offset
                buf += "$var wire %d %c %s $end\n" % (signal_dict[name], character_alias, name)
                offset += 1
            except OverflowError as e:
                print "Overflow Error: %s" % str(e)
                print "\tname: %s" % name
                print "\tcharacter alias: %s" % character_alias
                print "\toffset: %d" % offset
                print "\tsignal num: %d" % signal_dict[name]
                raise Exception

        #Pop of the scope stack
        buf += "\n"
        buf += "$upscope\n"
        buf += "$end\n"
        buf += "\n"

        #End the signal name defnitions
        buf += "$enddefinitions\n"
        buf += "$end\n"
        return buf

    def set_waveforms(self, data, signal_dict, add_clock, cycles_per_clock, debug = False):
        buf = ""
        buf += "#0\n"
        buf += "$dumpvars\n"
        timeval = 0

        if debug: print "Cycles per clock: %d" % cycles_per_clock

        index_offset = 33
        clock_character = 33
        if add_clock:
            index_offset = 34

        #Time 0
        #Add in the initial Clock Edge
        if add_clock:
            buf += "%d%c\n" % (0, clock_character)

        for i in range(len(signal_dict)):
            buf += "x%c\n" % (index_offset + i)

        #Time 1/2 clock cycle
        if add_clock:
            buf += "#%d\n" % (cycles_per_clock / 2)
            buf += "%d%c\n" % (0, clock_character)

        if add_clock:
            buf += "#%d\n" % ((i + 1) * cycles_per_clock)
            buf += "%d%c\n" % (1, clock_character)


        for j in range (len(signal_dict)):
            buf += "%d%c\n" % (((data[0] >> j) & 0x01), (index_offset + j))

        #Time 1/2 clock cycle
        if add_clock:
            buf += "#%d\n" % (cycles_per_clock / 2)
            buf += "%d%c\n" % (0, clock_character)



        #Go through all the values for every time instance and look for changes
        if debug: print "Data Length: %d" % len(data)
        for i in range(1, len(data)):

            if add_clock:
                buf += "#%d\n" % ((i + 1) * cycles_per_clock)
                buf += "%d%c\n" % (1, clock_character)

            #Read up to the second to the last peice of data
            if data[i - 1] != data[i]:
                if not add_clock:
                    buf += "#%d\n" % ((i + 1) * cycles_per_clock)
                for j in range (len(signal_dict)):
                    if ((data[i - 1] >> j) & 0x01) != ((data[i] >> j) & 0x01):
                        buf += "%d%c\n" % (((data[i] >> j) & 0x01), (index_offset + j))

            if add_clock:
                buf += "#%d\n" % (((i + 1) * cycles_per_clock) + (cycles_per_clock / 2))
                buf += "%d%c\n" % (0, clock_character)


        buf += "#%d\n" % (len(data) * cycles_per_clock)
        for i in range(len(signal_dict)):
            buf += "%d%c\n" % (((data[-1] >> i) & 0x01), (33 + i))
        return buf

    def create_vcd_buffer(self, data, signal_dict = OrderedDict(), count = 32, clock_count = 100, add_clock = True, debug = False):
        if debug: print "Create a VCD file"
        print "clock count: %d" % clock_count
        ghertz_freq = 1000000000
        if clock_count == 0:
            clock_count = 100000000
        cycles_per_clock = int(ghertz_freq / clock_count)
        if debug: print "Clocks per cycle: %d" % cycles_per_clock

        if len(signal_dict) < count:
            for i in range(count):
                signal_dict["signal%d" % i] = 1

        buf = ""
        buf += self.set_vcd_header()
        buf += self.set_signal_names(signal_dict, add_clock)
        buf += self.set_waveforms(data, signal_dict, add_clock, cycles_per_clock, debug)
        return buf

    def set_value(self, name, value):
        if name == TRIGGER:
            self.trigger = value
            self.log.info("Trigger: 0x%08X" % value)
        if name == TRIGGER_MASK:
            self.trigger_mask = value
            self.log.info("Trigger Mask: 0x%08X" % value)
        if name == TRIGGER_EDGE:
            self.trigger_edge = value
            self.log.info("Trigger Edge: 0x%08X" % value)
        if name == TRIGGER_BOTH_EDGE:
            self.both_edge
            self.log.info("Both Edge: 0x%08X" % value)
        if name == TRIGGER_REPEAT:
            self.trigger_repeat = value
            self.log.info("Repeat Count: 0x%08X" % value)
        if name == TRIGGER_AFTER:
            self.trigger_after = value
            self.log.info("Trigger After: 0x%08X" % value)
        if name == FORCE_TRIGGER:
            self.log.info("Force Trigger!")
        if name == SIZE:
            self.size = value
            self.log.info("Size: HEX: 0x%08X DEC: %d" % (value, value))
        if name == ENABLE:
            self.enable = value
            self.log.info("Enable: %s" % value)
        
        

