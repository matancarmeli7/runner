#!/usr/bin/python3
from subprocess import PIPE, run
from datetime import datetime
import pytest
import time
import runner

def test_should_run_cmd_n_times_succefully():
    total_return_codes = runner.create_runner(
        'ls -l', 3, 0, False, False, False, False)    
    assert total_return_codes == 3
    
def test_should_run_cmd_n_times_not_succefully():
    total_return_codes = runner.create_runner(
        'bad_command', 3, 2, False, False, False, False)    
    assert total_return_codes == 2
    
def test_should_create_log_file():
    correct_log_file = '{}'.format(datetime.now().strftime('runner_test_%H_%M_%d_%m_%Y.log'))
    log_file = runner.create_log_file(
        "runner_test")
    assert log_file == correct_log_file
    
def test_should_create_pcap_file():
    correct_pcap_file = '{}'.format(datetime.now().strftime('runner_test_%H_%M_%d_%m_%Y.pcap'))
    pcap_file = runner.create_pcap_file(
        "runner_test")
    assert pcap_file == correct_pcap_file
    
def test_should_create_log_file_and_check_if_sys_trace_option_works():
    correct_log_file = '{}'.format(datetime.now().strftime('runner_number_1_date_%H_%M_%d_%m_%Y.log'))
    runner.create_runner(
        'ls -l some_not_existing_file', 1, 0, True, False, False, False)
    test_command_output = run('grep cpu {0}; grep disk {0}; grep network {0}; grep memory {0}'\
                              .format(correct_log_file), shell=True)
    assert test_command_output.returncode == 0
    
def test_should_create_log_file_and_check_if_call_trace_option_works():
    correct_log_file = '{}'.format(datetime.now().strftime('runner_number_1_date_%H_%M_%d_%m_%Y.log'))
    runner.create_runner(
        'ls -l some_not_existing_file', 1, 0, False, True, False, False)
    test_command_output = run('grep "system calls" {}'\
                              .format(correct_log_file), shell=True)
    assert test_command_output.returncode == 0
    
def test_should_create_log_file_and_check_if_log_trace_option_works():
    correct_log_file = '{}'.format(datetime.now().strftime('runner_number_1_date_%H_%M_%d_%m_%Y.log'))
    runner.create_runner(
        'ls -l some_not_existing_file', 1, 0, False, False, True, False)
    test_command_output = run('grep stdout {}'\
                              .format(correct_log_file), shell=True)
    assert test_command_output.returncode == 0

def test_should_create_pcap_file_and_check_if_net_trace_option_works():
    correct_pcap_file = '{}'.format(datetime.now().strftime('runner_number_0_date_%H_%M_%d_%m_%Y.pcap'))
    runner.create_runner(
        'sleep 2; ls -l mm', 1, 0, False, False, False, True)
    test_command_output = run('tcpdump -r {}'\
                              .format(correct_pcap_file), shell=True)
    assert test_command_output.returncode == 0