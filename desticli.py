#!/usr/bin/python

import os
import logging
import argparse
import getpass
import requests
import pickle

import config
from destilib import auth
from destilib import items
from destilib import user

logging.basicConfig(level=logging.DEBUG)
ul3_logger = logging.getLogger("requests.packages.urllib3")
ul3_logger.setLevel(logging.WARN)

# Set up the CLI arguments and parse them
parser = argparse.ArgumentParser(description='Destiny Command Line Interface')
subparsers = parser.add_subparsers(help='Choose sub-command')

parser_normalize = subparsers.add_parser('normalize', help='Normalize stacks evenly across characters')
parser_normalize.add_argument('filter', choices=items.getItemCategories().keys(), nargs='+', help='Item filter')
parser_normalize.set_defaults(func=items.normalize)

args = parser.parse_args()

session = None

# Check if we can reuse cookies from the previous session
if os.path.isfile('cookies.bin'):
	cookies = None

	with open('cookies.bin', 'rb') as f:
		cookies = pickle.load(f)

	if not cookies:
		print "Failed to load cookies. Try again to authenticate."
		os.remove('cookies.bin')
		exit()

	session = requests.Session()
	session.cookies = cookies

	session.headers["X-API-Key"] = config.API_KEY
	session.headers["x-csrf"] = session.cookies["bungled"]
else:
	# Args are OK, time to authenticate
	username = config.USERNAME
	password = config.PASSWORD

	while not username:
		username = raw_input("Enter Username: ")
	while not password:
	   password = getpass.getpass("Enter Password: ")

	session = auth.login(username, password, config.API_KEY)
	
	if session:
		with open('cookies.bin', 'wb') as f:
			pickle.dump(session.cookies, f)

if not session:
	print "Failed to authenticate against PSN / Bungie. Wrong credentials?"
	exit()

# Authentication is complete, time to do some work
args.func(config, session, args)
