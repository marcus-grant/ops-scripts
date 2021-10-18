import pytest
import ddns
#  import os
import subprocess


def test_API_ENDPOINTS_default():
    assert ddns.API_ENDPOINT == 'https://api.cloudflare.com/client/v4'

#  def test_get_ip():
#      assert dd

def test_API_KEY_from_argparse():
    key_arg_stdout = subprocess.run([
            './ddns.py',
            '--key'
            'foobar-blahblah-123'
        ], capture_output=True)
    k_arg_stdout = subprocess.run([
            './ddns.py',
            '-k'
            'foobar-blahblah-123'
        ], capture_output=True)
    print(k_arg_stdout.stdout)


