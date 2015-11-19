#!/bin/python

import argparse
import os
import requests
import json

parser = argparse.ArgumentParser(description='Load dashboards from a directory into grafana')
parser.add_argument('-d','--dir', help='directory to search for saved dashboards', required=True)
parser.add_argument('-s','--server', help='server URL to push dashes to', default="http://127.0.0.1:3000")
parser.add_argument('-u','--user', help='basic auth user', default="admin")
parser.add_argument('-p','--pwd', help='basic auth password', default="admin")
parser.add_argument('-g','--graphite', help='graphite url')

args = parser.parse_args()

files = os.listdir(args.dir) 

server = args.server
auth = (args.user,args.pwd)

down = True
while down:
    try:
        requests.get(server + '/api/search', auth=auth).text
        down = False
    except:
        pass

def fail(r):
    print("failed for dash (" + str(r.status_code)+ ") " + f)
    print(r.text)

for f in files:
    with open(args.dir+'/'+f) as fh:
       r = requests.post(server + '/api/dashboards/db', data=fh, auth=auth,headers={"Content-Type":"application/json"})
       if r.status_code == requests.codes.ok:
            print("uploaded dash " + f)
       elif r.status_code == 404:
            fh.seek(0)
            d = json.load(fh)
            d["dashboard"]["id"]= None;
            r = requests.post(server + '/api/dashboards/db', json=d, auth=auth,headers={"Content-Type":"application/json"})
            if r.status_code == requests.codes.ok:
                print("created new dash " + f)
            else:
                fail(r)
       else:
            fail(r)


if args.graphite:
    r = requests.post(server + '/api/datasources', json={"name":"default","type":"graphite","url":str(args.graphite),"access":"proxy","basicAuth":False, "isDefault":True},                                                             auth=auth,headers={"Content-Type":"application/json"})
    if r.status_code == requests.codes.ok:
            print("Datasource set")
    else:
            print("failed to set datasource")
            print(r.text)
