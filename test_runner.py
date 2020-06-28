#!/usr/bin/python3
from subprocess import PIPE, run
from datetime import datetime
import pytest
import runner

def test_should_run_cmd_n_times_succefully():
    total_return_codes = runner.create_runner(
        'ls -l', 3, 0, False, False, False, False)    
    assert total_return_codes == 3