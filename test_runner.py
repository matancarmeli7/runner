#!/usr/bin/python3
from subprocess import PIPE, run
from datetime import datetime
import pytest
import runner

def test_should_run_cmd_n_times_succefully():
    total_return_codes = runner.create_runner(
        'ls -l', 3, 0, False, False, False, False)    
    assert total_return_codes == 3
    
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