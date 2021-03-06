#!/usr/bin/python3
from subprocess import PIPE, Popen
from datetime import datetime
from threading import Thread
from os import remove, path
import argparse
import logging
import psutil
import pdb
import signal
import time
import sys

# Defines what arguments the runner.py can get
def create_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Python script that wraps any other command and '
        'outputs a summary of execution')
    parser.add_argument(
        '-c',
        metavar='Count',
        default=1,
        type=int,
        help='Number of times to run the given command (default: 1)',
    )
    parser.add_argument(
        '--failed-count',
        metavar='N',
        type=int,
        default=0,
        help='Number of allowed failed command invocation attempts '
        'before givingup (default: 0)')
    parser.add_argument(
        '--sys-trace',
        action='store_const',
        const='True',
        help='Creates a log for each of the following values:\n'
        '  * Disk IO\n  * Memory\n  '
        '* Process & CPU usage of the command\n  * Network information')
    parser.add_argument(
        '--call-trace',
        action='store_const',
        const='True',
        help='For each failed execution, '
        'add to a log with all the system calls that ran by the command')
    parser.add_argument(
        '--log-trace',
        action='store_const',
        const='True',
        help='For each failed execution, '
        'add to a log the stdout and the stdin of the command')
    parser.add_argument(
        '--debug',
        action='store_const',
        const='True',
        help='Debug mode')
    parser.add_argument(
        '--net-trace',
        action='store_const',
        const='True',
        help='For each failed execution, '
        'create a ‘pcap’ file with the network traffic during the execution')
    args = parser.parse_args()

    if args.failed_count > args.c:
        parser.error(
            '--failed-count value must be equal or lower than -c value')

    if args.failed_count < 0:
        if args.c >= 0:
            parser.error('--failed-count must be equal or bigger that 0')
        parser.error('-c and --failed-count must be equal or bigger that 0')

    return args

# Execute the desired command
# Function Parameters: string (The command to execute), boolean (If the user choose the --call-trace option or not)
def run_command(command, call_trace):
    try:
        global pid
        global return_code
        global outs
        return_code = None
        pid = 0

        if call_trace:
            command = "strace -c {}".format(command)

        command_data = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        pid = command_data.pid
        command_process = psutil.Process(pid)

        if command_process.name() is 'sh':
            pid = command_process.children()[0].pid

        outs = command_data.communicate()
        return_code = command_data.returncode

    except OSError as error:
        print(error)

# Gets the command cpu usage and the threads that it runs
def get_command_cpu_usage_and_threads():
    global max_cpu
    global command_threads
    max_cpu = 0
    command_threads = {}

    while return_code is None:
        try:
            p = psutil.Process(pid)
            cpu_percent = p.cpu_percent(interval=0.1)

            if cpu_percent > max_cpu:
                max_cpu = cpu_percent

            for child in p.threads():
                if child.id not in command_threads.values():
                    child_p = psutil.Process(child.id)
                    command_threads.update({child_p.name(): child.id})

            time.sleep(0.5)
        except psutil.NoSuchProcess:
            pass

# Gets the total number of disk i\o
def get_total_disk_io():
    global disk_io_reads
    global disk_io_writes
    disk_io_reads = psutil.disk_io_counters().read_count
    disk_io_writes = psutil.disk_io_counters().write_count

# Gets the total network card package counters
def get_total_network_cards():
    global network_packets_sent
    global network_packets_recv
    network_packets_sent = psutil.net_io_counters().packets_sent
    network_packets_recv = psutil.net_io_counters().packets_recv

# Gets the used memory in the server
def get_memory():
    global memory
    memory = float("{:.2f}".format(psutil.virtual_memory().used / 1073741824))

# Creates the log file
# Function Parameters: string (the path of the log file, without date)
def create_log_file(log_file):
    log_file = '{}'.format(
        datetime.now().strftime(
            log_file +
            '_%H_%M_%d_%m_%Y.log'))
    if path.exists(log_file):
        remove(log_file)
    global logger
    logger = logging.getLogger('runner{}'.format(num_of_failed_commands))
    hdlr = logging.FileHandler('{}'.format(log_file))
    print(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    # For test purpose
    return log_file

# Write an error message to the log file
# Function Parameters: string (the message to write to the log file)
def write_error_log(message):
    logger.error(message)

# Write an info message to the log file
# Function Parameters: string (the message to write to the log file)
def write_info_log(message):
    logger.info(message)

# Creates pcap file
# Function Parameters: string (the path of the pcap file, without date)
def create_pcap_file(pcap_file_name):
    pcap_file_name = '{}'.format(
        datetime.now().strftime(
            pcap_file_name +
            '_%H_%M_%d_%m_%Y.pcap'))

    if path.exists(pcap_file_name):
        remove(pcap_file_name)

    f = open(pcap_file_name, "a")
    f.close()
    print(pcap_file_name)
    return pcap_file_name

# Create a ‘pcap’ file with the network traffic during the execution.
# Function Parameters: Thread (The thread object that execute the desired command), string (the path of the pcap file)
def write_net_trace(command_thread, pcap_file_name):
    pcap_file_name = create_pcap_file(pcap_file_name)
    tcpdump_command = 'tcpdump -w {}'.format(pcap_file_name)
    tcpdump_command_data = Popen(
        tcpdump_command.split(),
        stdout=PIPE,
        stderr=PIPE)
    command_thread.join()
    tcpdump_command_data.terminate()

    if return_code == 0:
        remove(pcap_file_name)

# Print statistics on the return codes
def print_statistics():
    print("--- {} command statistics ---".format(command))
    print(
        "{} commands executed, {} succeeded and {} failed" .format(
            executed_commands,
            executed_commands -
            num_of_failed_commands,
            num_of_failed_commands))
"""
Handle ctrl+c
Function Parameters: int(The type of the signal that sent to the script), 
frame (It point to the frame that was interrupted by the signal)
"""
def signal_handler(sig, frame):
    print("Program was interrupted by Ctrl+C!")
    print_statistics()
    sys.exit(0)

""" 
Function that run the desired comand and adds fitures if needed.
Function Parameters: string (The command to execute), int (The number of times to execute the command), 
int (The number of times that the command can fail), boolean (If the user choose the --sys-trace option or not),
boolean (If the user choose the --call-trace option or not), boolean (If the user choose the --log-trace option or not),
boolean (If the user choose the --net-trace option or not) and boolean (If the user choose the --debug option or not)
"""
def create_runner(
        command,
        command_num,
        failed,
        sys_trace = False,
        call_trace = False,
        log_trace = False,
        net_trace = False,
        debug = False):
    global num_of_failed_commands
    num_of_failed_commands = 0
    global executed_commands
    executed_commands = 0

    for _ in range(command_num):
        command_thread = Thread(
            target=run_command, args=(
                command, call_trace))
        command_thread.start()
        executed_commands += 1

        if sys_trace:
            functions = [
                get_command_cpu_usage_and_threads,
                get_total_disk_io,
                get_total_network_cards,
                get_memory]
            threads = []

            for function in range(len(functions)):
                threads.append(Thread(target=functions[function]))
                threads[function].start()

            for thread in threads:
                thread.join()

        if net_trace:
            pcap_file_name = 'runner_number_{}_date'.format(
                num_of_failed_commands)
            write_net_trace(command_thread, pcap_file_name)
        else:
            command_thread.join()

        if return_code != 0:
            num_of_failed_commands += 1

            if sys_trace or call_trace or log_trace:

                if debug:
                    pdb.set_trace()

                log_file = 'runner_number_{}_date'.format(
                    num_of_failed_commands)
                create_log_file(log_file)

                if call_trace:

                    if len(str(outs[1]).split("% time")) > 1:
                        message = 'system calls of the commad: {}'\
                                  .format(str(outs[1]).split("% time")[1])
                        write_error_log(message)
                    else:
                        message = '{} and therfore there is no system calls'\
                            .format(outs[1])
                        write_error_log(message)

                if log_trace:
                    message = 'The stdout of the command is: {}, '
                    'the stderr of the command is: {}'\
                        .format(str(outs[0]),
                                str(outs[1]).split("% time")[0])
                    write_error_log(message)

                if sys_trace:
                    cpu_and_threads_message = 'cpu usage of the command: {}, '
                    'and the threads that it runs are: {}'\
                        .format(
                            max_cpu,
                            command_threads)
                    write_info_log(cpu_and_threads_message)
                    disk_io_message = 'Number of disk io reads: {}, '
                    'Number of disk io writes: {}, '
                    'Total number of disk io: {}'\
                        .format(
                            disk_io_reads,
                            disk_io_writes,
                            disk_io_reads + disk_io_writes)
                    write_info_log(disk_io_message)
                    network_message = 'Number of network packets sent: {}, '
                    'Number of packets recived: {}, '
                    'Total number of network packets: {}'\
                        .format(network_packets_sent,
                                network_packets_recv,
                                network_packets_sent + network_packets_recv)
                    write_info_log(network_message)
                    memory_message = "The used memory is: {}".format(memory)
                    write_info_log(memory_message)
            else:
                if debug:
                    pdb.set_trace()

        else:
            if debug:
                pdb.set_trace()

        if (num_of_failed_commands == failed and
                num_of_failed_commands != 0):
            print("The execution of the command failed for {} times".format(
                num_of_failed_commands))
            # For test purpose
            return executed_commands
        # For test purpose
        if executed_commands == command_num:
            return executed_commands


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    args = create_arguments()
    command = input("Enter your command: ")

    if args.debug:
        pdb.set_trace()

    create_runner(
        command,
        args.c,
        args.failed_count,
        args.sys_trace,
        args.call_trace,
        args.log_trace,
        args.net_trace,
        args.debug)
    print_statistics()
