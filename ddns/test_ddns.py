import pytest
import ddns
#  import os
import subprocess
import http
#  import BaseHTTPServer
import httpretty


# TODO need more complete testing
def test_API_ENDPOINTS_default():
    assert ddns.API_ENDPOINT == 'https://api.cloudflare.com/client/v4'

#  def test_request_default():
#      http.server.HTTPServer(('localhost', 42069), )
#      ip = main.request_ip('http://localhost:42069')

#  @httpretty.activate
#  def test_check_response():
#      httpretty.register_uri()




#  @pytest.mark.parametrize("key", ["abc", "skip"])
#  @pytest.mark.parametrize("zone", ["skip", "foobar.com"])
#  @pytest.mark.parametrize("user", ["bobsmith@mail.io", "janedoe"])
#  @pytest.mark.parametrize("endpoint", ["skip", "localhost:9387"])
#  @pytest.mark.parametrize("expected", [
#
#  ])
#  def test_request_format_from_args():
#       = subprocess.run([
#              './ddns.py',
#              '-k'
#              'foobar-blahblah-123'
#          ], capture_output=True)
#      print(k_arg_stdout.stdout)


