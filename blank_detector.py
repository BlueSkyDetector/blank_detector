#!/usr/bin/env python3

import ctypes
import struct
from logging import getLogger, StreamHandler, FileHandler, Formatter, INFO
import subprocess
import select
import threading
import time
import os
import signal

logger = getLogger(__name__)
formatter = Formatter('%(asctime)s - %(levelname)s: %(message)s',
                      '%Y/%m/%d %H:%M:%S')
handler = StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)

ctypes.cdll.LoadLibrary('libXext.so')
libXext = ctypes.CDLL('libXext.so')

DPMSFAIL = -1
DPMSModeOn = 0
DPMSModeStandby = 1
DPMSModeSuspend = 2
DPMSModeOff = 3

STREAM_TYPE_STDOUT = 'stdout'
STREAM_TYPE_STDERR = 'stderr'


def get_DPMS_state(display_name_in_byte_string=b':0'):
    state = DPMSFAIL
    if not isinstance(display_name_in_byte_string, bytes):
        raise TypeError
    display_name = ctypes.c_char_p()
    display_name.value = display_name_in_byte_string
    libXext.XOpenDisplay.restype = ctypes.c_void_p
    display = ctypes.c_void_p(libXext.XOpenDisplay(display_name))
    dummy1_i_p = ctypes.create_string_buffer(8)
    dummy2_i_p = ctypes.create_string_buffer(8)
    if display.value:
        if libXext.DPMSQueryExtension(display, dummy1_i_p, dummy2_i_p)\
           and libXext.DPMSCapable(display):
            onoff_p = ctypes.create_string_buffer(1)
            state_p = ctypes.create_string_buffer(2)
            if libXext.DPMSInfo(display, state_p, onoff_p):
                onoff = struct.unpack('B', onoff_p.raw)[0]
                if onoff:
                    state = struct.unpack('H', state_p.raw)[0]
        libXext.XCloseDisplay(display)
    return state


class Worker(threading.Thread):
    def __init__(self, cmd, func_for_stdout, func_for_stderr, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.daemon = True
        self.cmd = cmd
        self.func_for_stdout = func_for_stdout
        self.func_for_stderr = func_for_stderr
        self.subproc = None

    def run(self):
        self.subproc = subprocess.Popen(self.cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        shell=True,
                                        universal_newlines=True,
                                        preexec_fn=os.setsid)

        def getfd(s):
            return s.fileno()
        while True:
            reads = [getfd(self.subproc.stdout), getfd(self.subproc.stderr)]
            ret = select.select(reads, [], [])

            for fd in ret[0]:
                if fd == getfd(self.subproc.stdout):
                    read = self.subproc.stdout.readline()
                    self.func_for_stdout(read, STREAM_TYPE_STDOUT)
                if fd == getfd(self.subproc.stderr):
                    read = self.subproc.stderr.readline()
                    self.func_for_stderr(read, STREAM_TYPE_STDERR)

            if self.subproc.poll() is not None:
                break

    def terminate(self):
        os.killpg(os.getpgid(self.subproc.pid), signal.SIGTERM)
        self.subproc.terminate()


class TaskController(object):

    def __init__(self,
                 cmd,
                 func_for_stdout=None,
                 func_for_stderr=None):
        self.__is_running = False
        self.cmd = cmd
        if func_for_stdout is None:
            self.func_for_stdout = self.default_func_for_stream
        else:
            self.func_for_stdout = func_for_stdout
        if func_for_stderr is None:
            self.func_for_stderr = self.default_func_for_stream
        else:
            self.func_for_stderr = func_for_stderr

    def default_func_for_stream(self, cmd_output, stream_type):
        if cmd_output == '':
            return
        elif stream_type == STREAM_TYPE_STDOUT:
            logger.info('STDOUT: ' + cmd_output.rstrip('\r\n'))
        elif stream_type == STREAM_TYPE_STDERR:
            logger.warning('STDERR: ' + cmd_output.rstrip('\r\n'))

    def is_running(self):
        return self.__is_running

    def start(self):
        logger.info('Starting \'%s\'...' % self.cmd)
        if self.__is_running is False:
            self.__process = Worker(self.cmd,
                                    self.func_for_stdout,
                                    self.func_for_stderr)
            self.__process.start()
            self.__is_running = True
            logger.info('Started.')
        else:
            logger.info('Already started. Nothing to do.')

    def stop(self):
        logger.info('Stopping \'%s\'...' % self.cmd)
        if self.__is_running is True:
            self.__process.terminate()
            self.__is_running = False
            logger.info('Stopped.')
        else:
            logger.info('Already stopped. Nothing to do.')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        '--display',
                        action='store',
                        required=True,
                        help='For detecting display blank, '
                             'specify target display name in format \':0.0\'')
    parser.add_argument('-c',
                        '--command',
                        action='store',
                        required=True,
                        help='Set a command to execute')
    parser.add_argument('-l',
                        '--log',
                        action='store',
                        help='Set log file path for logging')
    args = parser.parse_args()
    if args.log:
        file_handler = FileHandler(args.log)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(INFO)
        logger.handlers = []
        logger.addHandler(file_handler)

    logger.info('#' * 80)
    logger.info('############# \'%s\' started #############' % __file__)
    display_name_in_byte_string = args.display.encode('ascii')
    dpms_state = DPMSFAIL
    task = TaskController(args.command)
    try:
        while True:
            new_dpms_state = get_DPMS_state(display_name_in_byte_string)
            if dpms_state != new_dpms_state:
                dpms_state = new_dpms_state
                if dpms_state == DPMSFAIL:
                    logger.info(
                        'DPMS state of \'%s\' is detected as [DPMSFAIL]'
                        % args.display)
                    if task.is_running():
                        task.stop()
                elif dpms_state == DPMSModeOn:
                    logger.info(
                        'DPMS state of \'%s\' is detected as [DPMSModeOn]'
                        % args.display)
                    if task.is_running():
                        task.stop()
                elif dpms_state == DPMSModeStandby:
                    logger.info(
                        'DPMS state of \'%s\' is detected as [DPMSModeStandby]'
                        % args.display)
                    if not task.is_running():
                        task.start()
                elif dpms_state == DPMSModeSuspend:
                    logger.info(
                        'DPMS state of \'%s\' is detected as [DPMSModeSuspend]'
                        % args.display)
                    if not task.is_running():
                        task.start()
                elif dpms_state == DPMSModeOff:
                    logger.info(
                        'DPMS state of \'%s\' is detected as [DPMSModeOff]'
                        % args.display)
                    if not task.is_running():
                        task.start()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Keyboard Interrupted...')
    finally:
        if task.is_running():
            task.stop()
        logger.info('############# \'%s\' terminating #############'
                    % __file__)
        logger.info('#' * 80)


if __name__ == '__main__':
    main()
