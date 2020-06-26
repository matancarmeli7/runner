#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
    description='Python script that wraps any other command and outputs a summary of execution')
parser.add_argument('-c', metavar='Count', default=1, type=int, nargs=1,
                    help= 'Number of times to run the given command',)
parser.add_argument('--failed-count', metavar='N', type=int, nargs=1,
                    help= 'Number of allowed failed command invocation attempts before givingup')
parser.add_argument('--sys-trace', metavar='',
                    help= 'Creates a log for each of the following values:\n'
                    '  * Disk IO\n  * Memory\n  * Process & CPU usage of the command\n  * Network information')
parser.add_argument('--call-trace', metavar='',
                    help= 'For each failed execution, add to a log with all the system calls that ran by the command')
parser.add_argument('--log-trace', metavar='',
                    help= 'For each failed execution, add to a log the stdout and the stdin of the command')
parser.add_argument('--debug', metavar='',
                    help= 'Debug mode')

args = parser.parse_args()
command = input("Enter your command: ")