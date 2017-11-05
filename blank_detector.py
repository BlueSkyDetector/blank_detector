#!/usr/bin/env python

import ctypes
import struct

ctypes.cdll.LoadLibrary('libXext.so')
libXext = ctypes.CDLL('libXext.so')

DPMSFAIL = -1
DPMSModeOn = 0
DPMSModeStandby = 1
DPMSModeSuspend = 2
DPMSModeOff = 3

display_name = ctypes.c_char_p()
display_name.value = b':0'


def get_DPMS_state():
    state = DPMSFAIL
    libXext.XOpenDisplay.restype = ctypes.c_void_p
    display = ctypes.c_void_p(libXext.XOpenDisplay(display_name))
    dummy1_i_p = ctypes.create_string_buffer(8)
    dummy2_i_p = ctypes.create_string_buffer(8)
    if display:
        if libXext.DPMSQueryExtension(display, dummy1_i_p, dummy2_i_p)\
            and libXext.DPMSCapable(display):
                onoff_p = ctypes.create_string_buffer(1)
                state_p = ctypes.create_string_buffer(2)
                if libXext.DPMSInfo(display, state_p, onoff_p):
                    onoff = struct.unpack('B', onoff_p.raw)[0]
                    #onoff = int.from_bytes(onoff_p.raw, byteorder='little') # After Python 3.2
                    if onoff:
                        state = struct.unpack('H', state_p.raw)[0]
                        #state = int.from_bytes(state_p.raw, byteorder='little')
        libXext.XCloseDisplay(display)
    return state

import time
while True:
    print(time.strftime('%Y/%m/%d %H:%M:%S') + ': ' + str(get_DPMS_state()))
    time.sleep(1)
