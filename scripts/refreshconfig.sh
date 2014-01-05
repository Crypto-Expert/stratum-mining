#!/usr/bin/env python
# Send notification to Stratum mining instance add a new litecoind instance to the pool

import socket
import json
import sys
import argparse
import time

start = time.time()

parser = argparse.ArgumentParser(description='Refresh the config of the Stratum instance.')
parser.add_argument('--password', dest='password', type=str, help='use admin password from Stratum server config')
parser.add_argument('--host', dest='host', type=str, default='localhost', help='hostname of Stratum mining instance')
parser.add_argument('--port', dest='port', type=int, default=3333, help='port of Stratum mining instance')
args = parser.parse_args()

if args.password == None:
	parser.print_help()
	sys.exit()
	
message = {'id': 1, 'method': 'mining.refresh_config', 'params': []}

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port))
    s.sendall(json.dumps(message)+"\n")
    data = s.recv(16000)
    s.close()
except IOError:
    print "Refresh Config: Cannot connect to the pool"
    sys.exit()

for line in data.split("\n"):
    if not line.strip():
    	# Skip last line which doesn't contain any message
        continue

    message = json.loads(line)
    if message['id'] == 1:
        if message['result'] == True:
	        print "Refresh Config: done in %.03f sec" % (time.time() - start)
        else:
            print "Refresh Config: Error during request:", message['error'][1]
    else:
        print "Refresh Config: Unexpected message from the server:", message
