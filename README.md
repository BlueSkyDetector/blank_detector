# blank_detector

A tool to detect blank screen by DPMS and run commands.

## Requirement

- Linux
- DPMS enabled X environment (Please check by 'xset q|grep DPMS')
- Python 2.7 or 3.x

## Usage

```
$ ./blank_detector.py -h
usage: blank_detector.py [-h] -d DISPLAY -c COMMAND [-l LOG]

optional arguments:
  -h, --help            show this help message and exit
  -d DISPLAY, --display DISPLAY
                        Specify display name in format ':0.0'
  -c COMMAND, --command COMMAND
                        Set a command to execute
  -l LOG, --log LOG     Set log file path for logging
```

## Example

```
$ ./blank_detector.py -d ':0.0' -c 'command.sh arg1 arg2' -l /path/to/app.log
```
