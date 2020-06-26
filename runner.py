#!/usr/bin/python3
import argparse
from subprocess import run, PIPE

# Defines what arguments the runner.py can get
def create_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description='Python script that wraps any other command and outputs a summary of execution')
    parser.add_argument('-c', metavar='Count', default=1, type=int,
                        help= 'Number of times to run the given command (default: 1)',)
    parser.add_argument('--failed-count', metavar='N', type=int, default=0,
                        help= 'Number of allowed failed command invocation attempts before givingup (default: 1)')
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

    if args.failed_count > args.c:
        parser.error('--failed-count value must be equal or lower than -c value')

    if args.failed_count < 0:
        if args.c >= 0:
            parser.error('--failed-count must be equal or bigger that 0')
        parser.error('-c and --failed-count must be equal or bigger that 0')

    return args

def exec_command(command):
    process = run(command.split(), stdout=PIPE, stderr=PIPE)
    print(process.stdout)

if __name__ == "__main__":
    args = create_arguments()
    command = input("Enter your command: ")
    for i in range(args.c):
        exec_command(command)