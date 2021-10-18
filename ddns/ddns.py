#! /usr/bin/env python3
# TODO: Implement configuration parsing
# import yaml
# imports for os/path and sys/exit
import argparse
import configparser
import http.client
import json
import logging
import os
import socket
import sys

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
        help="The URL to the API endpoint for the DNS service"
    )
    parser.add_argument(
        "-i",
        "--ipserver",
        default="myip.marcusfg.workers.dev",
        help="A request URL that returns your public IP as plaintext"
    )
    parser.add_argument(
        "-s",
        "--subdomain",
        default="@",
        help="A subdomain with or without regex pattern to match to, defaults to root (@)"
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
    print(shell_args)
    config_args = parse_config(shell_args['config'])
    if config_args == None:
        return shell_args
    args_keys = ['key', 'zone', 'user', 'endpoint', 'ipserver', 'subdomain']
    merged_args = {}
    for key in args_keys:
        merged_args[key] = config_args[key]
        if not not shell_args[key]:
            merged_args[key] = shell_args[key]
    return merged_args

# TODO: turn headers into all lower case and make checks for contenttypes
def request_ip(myip_url):
    conn = http.client.HTTPSConnection(myip_url)
    conn.request("GET", "/")
    resp = conn.getresponse()
    if resp.status != 200:
        sys.exit("ERROR: Could not get IP from server {} with reason {}"
            .format(myip_url, resp.reason))
    headers = resp.getheaders()
    contenttype = None
    for header in headers:
        if header[0] == 'Content-Type':
            contenttype = header[1]
    if 'text/plain' not in contenttype:
        sys.exit("ERROR: Content-Type header of IP server not supported")
    public_ip = resp.read()
    # TODO get it to read charset to set decode type
    # NOTE OR figure out why it sends bytes instead of strings
    if type(public_ip) is bytes:
        public_ip = public_ip.decode('utf-8')
    return public_ip

def check_response(response) -> list:
    res = json.loads(response.read().decode('utf-8'))
    if (not res['success']):
        print('ERROR: No success requesting Cloudflare API: {} - {}'
            .format(
                str(res['errors'][0]['code']),
                res['errors'][0]['message']
            )
        )
        sys.exit(1)
    return res['result']

# TODO decide how this can be made more generic
def request_cloudflare(headers, query, method='GET', payload='') -> list:
    if type(payload) is dict:
        payload = json.dumps(payload)
    conn = http.client.HTTPSConnection('api.cloudflare.com')
    try:
        conn.request(method, query, payload, headers)
        res = conn.getresponse()
    except Exception as e:
        print(str(e))
        sys.exit(1)
    res = check_response(res)
    return res

# NOTE X-Auth-Key seems to work better than bearer in Auth
def get_cloudflare_auth_header(args: dict) -> dict:
    return {
        'X-Auth-Email': args['user'],
        'X-Auth-Key': '{}'.format(args['key']),
        # 'Authorization': 'Bearer {}'.format(args['key']),
    }

# TODO Refactor a way to get rid of constant args passing
def request_cloudflare_zones(args):
    return request_cloudflare(
        get_cloudflare_auth_header(args),
        '/client/v4/zones'
    )

def request_cloudflare_zoneid(args):
    """ Using the request_cloudflare_zones query and 
        script 'args' containing a zone name,
        return the zone ID for that DNS zone name inside args.
    """
    zones_res = request_cloudflare_zones(args)
    for zone in zones_res:
        if zone['name'] == args['zone']:
            return zone['id']
    return None

def request_cloudflare_dns(zoneid, args):
    return request_cloudflare(
        get_cloudflare_auth_header(args),
        '/client/v4/zones/{}/dns_records?type=A&name={}'.format(zoneid,args['zone']),
    )

def get_recordid_from_dns(dns_records):
    return dns_records[0]['id']

def request_cloudflare_new_dns(zoneid, ip, args):
    subdomain = args['subdomain']
    if (subdomain is None) or (subdomain == '@'):
        subdomain = ''
    else:
        subdomain = '{}.'.format(subdomain)
    return request_cloudflare(
        get_cloudflare_auth_header(args),
        '/client/v4/zones/{}/dns_records'.format(zoneid),
        method='POST',
        payload={
            'type': 'A',
            'name': '{}{}'.format(subdomain, args['zone']),
            'content': ip,
            'ttl':  300,
        },
    )

def request_cloudflare_update_dns(zoneid, recordid, ip, args):
    subdomain = args['subdomain']
    if (subdomain is None) or (subdomain == '@'):
        subdomain = ''
    else:
        subdomain = '{}.'.format(subdomain)
    return request_cloudflare(
        get_cloudflare_auth_header(args),
        '/client/v4/zones/{}/dns_records/{}'
            .format(zoneid, recordid),
        method='PUT',
        payload={
            'type': 'A',
            'name': '{}{}'.format(subdomain, args['zone']),
            'content': ip,
            'ttl':  300,
        },
    )

def main():
    args = merge_config_and_shell_args()
    if not (args['key'] and args['user']):
        print(('ERROR: No API key for DNS service given.'
            'Please provide a valid API key for your DNS.'
        ))
        sys.exit(1)

    ip = request_ip(args['ipserver'])
    # TODO move this into seperate function
    listedip = socket.gethostbyname(args['zone'])
    if ip == listedip:
        print('Current IP {} is already listed on public DNS records'.format(ip))
        sys.exit(0)

    zoneid = request_cloudflare_zoneid(args)
    if not zoneid:
        print('ERROR: No CloudFlare zone exists of name {}.'
            .format(args['zone']))
        sys.exit(1)
    
    dns_records = request_cloudflare_dns(zoneid, args)
    dns_change_resp = {}
    if len(dns_records) < 1:
        dns_change_resp = request_cloudflare_new_dns(zoneid, ip, args)
    else:
        dns_recordid = get_recordid_from_dns(dns_records)
        dns_change_resp = request_cloudflare_update_dns(
            zoneid,
            dns_recordid,
            ip,
            args)
    print('Successfully changed {} A record to {}'
        .format(dns_change_resp['zone_name'], ip))


if __name__ == "__main__":
    main()
