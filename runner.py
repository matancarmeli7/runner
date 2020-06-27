#!/usr/bin/python3
import argparse
from subprocess import PIPE, Popen
import logging
from datetime import datetime
import psutil
from multiprocessing import Process, Queue

# Defines what arguments the runner.py can get
def create_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description='Python script that wraps any other command and outputs a summary of execution')
    parser.add_argument('-c', metavar='Count', default=1, type=int,
                        help= 'Number of times to run the given command (default: 1)',)
    parser.add_argument('--failed-count', metavar='N', type=int, default=0,
                        help= 'Number of allowed failed command invocation attempts before givingup (default: 1)')
    parser.add_argument('--sys-trace', metavar='', action='store_const', const="True",
                        help= 'Creates a log for each of the following values:\n'
                              '  * Disk IO\n  * Memory\n  * Process & CPU usage of the command\n  * Network information')
    parser.add_argument('--call-trace', metavar='', action='store_const', const="True",
                        help= 'For each failed execution, add to a log with all the system calls that ran by the command')
    parser.add_argument('--log-trace', metavar='', action='store_const', const="True",
                        help= 'For each failed execution, add to a log the stdout and the stdin of the command')
    parser.add_argument('--debug', metavar='', action='store_const', const="True",
                        help= 'Debug mode')
    args = parser.parse_args()

    if args.failed_count > args.c:
        parser.error('--failed-count value must be equal or lower than -c value')

    if args.failed_count < 0:
        if args.c >= 0:
            parser.error('--failed-count must be equal or bigger that 0')
        parser.error('-c and --failed-count must be equal or bigger that 0')

    return args

# Execute the desired command 
def run_command(command, q):
    command_data = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    q.put(str(command_data.pid))
    _, _ = command_data.communicate()
    q_retun_code.put(str(command_data.returncode))
    
def get_command_cpu_usage_and_threads():
    try:
        p = psutil.Process(int(q.get()))
        message = 'cpu usage of the command: {}, and the threads that it runs are: {}'\
                  .format(p.cpu_percent(), p.threads())
        write_info_log(message)
    except psutil.NoSuchProcess:
        print("The execution of the command was too fast")
        
def get_total_disk_io():
    disk_io_reads = psutil.disk_io_counters().read_count
    disk_io_writes = psutil.disk_io_counters().write_count
    message = 'Number of disk io reads: {}, Number of disk io writes: {}, Total number of disk io: {}'\
              .format(disk_io_reads, disk_io_writes, disk_io_reads+disk_io_writes)
    write_info_log(message)
    
def get_total_network_cards():
    network_packets_sent = psutil.net_io_counters().packets_sent
    network_packets_recv = psutil.net_io_counters().packets_recv
    message = 'Number of network packets sent: {}, Number of packets recived: {}, Total number of network packets: {}'\
              .format(network_packets_sent, network_packets_recv, network_packets_sent+network_packets_recv)
    write_info_log(message)

def get_memory():
    memory = float("{:.2f}".format(psutil.virtual_memory().used/1073741824))
    message = "The used memory is: {}".format(memory)
    write_info_log(message)
    

# Creates the log file
def create_log_file():
    global logger
    logger = logging.getLogger('runner')
    hdlr = logging.FileHandler('{}'.format(datetime.now().strftime('/home/matan/runner_%H_%M_%d_%m_%Y.log')))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

# write an error message to the log file
def write_error_log(message):
    logger.error(message)

# write an info message to the log file
def write_info_log(message):
    logger.info(message)
    
def create_runner(command, command_num, failed):
    num_of_failed_commands = 0
    for _ in range(command_num):
        command_process = Process(target=run_command, args=(command,q))
        command_process.start()
        
        if args.sys_trace:
            functions = [
                    get_command_cpu_usage_and_threads,
                    get_total_disk_io, 
                    get_total_network_cards, 
                    get_memory]
            processes = []
            for function in range(len(functions)):
                processes.append(Process(target=functions[function]))
                processes[function].start()
                
            for process in processes:
                process.join()
             
        command_process.join
        return_code = int(q_retun_code.get())
        if return_code != 0:
            num_of_failed_commands += 1
        if (num_of_failed_commands == failed and
            num_of_failed_commands != 0):
            print("The execution of the command failed for {} times".format(num_of_failed_commands))
            break   

if __name__ == "__main__":
    args = create_arguments()
    command = input("Enter your command: ")
    q = Queue()
    q_retun_code = Queue()
    if args.sys_trace or args.call_trace or args.log_trace:
        create_log_file()
    create_runner(command, args.c, args.failed_count)