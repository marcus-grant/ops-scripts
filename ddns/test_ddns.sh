#!/bin/bash

HOSTNAME="@"
DOMAIN="kungsten.cloud"
PASSWORD=`cat secrets.txt`

# IP=`curl -s ipecho.net/plain`
IP=`dig +short myip.opendns.com @resolver1.opendns.com`


request_str="https://dynamicdns.park-your-domain.com/update?host=$HOSTNAME&domain=$DOMAIN&password=$PASSWORD&ip=$IP"
# request_str="https://dynamicdns.park-your-domain.com/update?domain=$DOMAIN&password=$PASSWORD&ip=$IP"

echo $request_str 
curl "$request_str"
