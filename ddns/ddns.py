#! /usr/bin/env python3
# TODO: Implement configuration parsing
# import yaml
# imports for os/path and sys/exit
import logging
import argparse
import configparser
import http
import os

# TODO: Add request headers options
API_HEADERS = {}
API_ENDPOINT = 'https://api.cloudflare.com/client/v4'
CFG_PATH = '/etc/ddns/ddns.conf'

USAGE_DESCRIPTION = ("Use dynamic DNS services to update their DNS records "
        "with this hosts' publicly accessible IP address. "
        "Currently, only CloudFlare is supported")

def parse_args():
    parser = argparse.ArgumentParser('ddns', description=USAGE_DESCRIPTION)
    parser.add_argument(
        "-k",
        "--key",
        help="The API key to the dynamic DNS service",
    )
    parser.add_argument(
        "-z",
        "--zone",
        help="The Zone-ID or URL you're using (subdomain.domain.com)"
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Username or login email for the DNS service"
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        default=API_ENDPOINT,
        help="The URL to the API endpoint for the DNS service"
    )
    parser.add_argument(
        "-c",
        "--config",
        default=CFG_PATH,
        help="Specific config file to read from"
    )
    #  parser.add_argument...
    # Create parser here
    return parser.parse_args()

# TODO implement and test this
def parse_config(path):
    if not os.path.exists(path):
        return None
    config = configparser.ConfigParser()
    config.read(path)
    return config['default']

def merge_config_and_shell_args():
    shell_args = vars(parse_args())
    config_args = parse_config(shell_args['config'])
    if config_args == None:
        return shell_args
    args_keys = ['key', 'zone', 'user', 'endpoint']
    merged_args = {}
    for key in args_keys:
        merged_args[key] = config_args[key]
        if not not shell_args[key]:
            merged_args[key] = shell_args[key]
    return merged_args
    

def main():
    args = merge_config_and_shell_args()
    print(args)


if __name__ == "__main__":
    main()
