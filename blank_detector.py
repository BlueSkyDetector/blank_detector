#!/usr/bin/env python

import ctypes
import struct

ctypes.cdll.LoadLibrary("libXext.so")
libXext = ctypes.CDLL("libXext.so")

DPMSFAIL = -1
DPMSModeOn = 0
DPMSModeStandby = 1
DPMSModeSuspend = 2
DPMSModeOff = 3


def get_DPMS_state():
    state = DPMSFAIL
    Display = libXext.XOpenDisplay(0)
    dummy1_i_p = ctypes.create_string_buffer(8)
    dummy2_i_p = ctypes.create_string_buffer(8)
    if Display\
        and libXext.DPMSQueryExtension(Display, dummy1_i_p, dummy2_i_p)\
        and libXext.DPMSCapable(Display):
            onoff_p = ctypes.create_string_buffer(1)
            state_p = ctypes.create_string_buffer(2)
            if libXext.DPMSInfo(Display, state_p, onoff_p):
                onoff = struct.unpack('B', onoff_p.raw)[0]
                #onoff = int.from_bytes(onoff_p.raw, byteorder='little') # After Python 3.2
                if onoff:
                    state = struct.unpack('H', state_p.raw)[0]
                    #state = int.from_bytes(state_p.raw, byteorder='little')
    return state

import time
while True:
    print(time.strftime("%Y/%m/%d %H:%M:%S") + ": " + str(get_DPMS_state()))
    time.sleep(1)
