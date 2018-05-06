# Blank Detector Task Controller

A tool for running commands only when the display is blank or locked.

## Requirement

- Linux
- Python 2.7 or 3.x
- One of these for display status detector
    - DPMS enabled X environment (Please check by 'xset q|grep DPMS')
    - 'xscreensaver-command' for xscreensaver status

## Usage

```
$ ./blank_detector.py -h
usage: blank_detector.py [-h] [-d DISPLAY] -c COMMAND
                         [-m {DpmsDetector,XscreensaverDetector}] [-l LOG]

optional arguments:
  -h, --help            show this help message and exit
  -d DISPLAY, --display DISPLAY
                        For detecting display blank, specify target display
                        name in format ':0.0' (default is taken from $DISPLAY)
  -c COMMAND, --command COMMAND
                        Set a command to execute
  -m {DpmsDetector,XscreensaverDetector}, --module {DpmsDetector,XscreensaverDetector}
                        Select detector module for display status (default:
                        DpmsDetector)
  -l LOG, --log LOG     Set log file path for logging
```

## Example

```
$ ./blank_detector.py -d ':0.0' -c 'command.sh arg1 arg2' -m DpmsDetector -l /path/to/app.log
```

```
$ ./blank_detector.py -d ':0.0' -c 'command.sh arg1 arg2' -m XscreensaverDetector -l /path/to/app.log
```
