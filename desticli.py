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
from destilib import vendor

logging.basicConfig(level=logging.WARN)

# Set up the CLI arguments and parse them
parser = argparse.ArgumentParser(description='Destiny Command Line Interface')
subparsers = parser.add_subparsers(help='Choose sub-command')

parser_normalize = subparsers.add_parser('normalize', help='Normalize stacks evenly across characters')
parser_normalize.add_argument('filter', choices=items.getItemCategories().keys(), nargs='+', help='Item filter')
parser_normalize.set_defaults(func=items.normalize)

parser_move = subparsers.add_parser('move', help='Move stacks to the vault')
parser_move.add_argument('destination', choices=['vault'], help='Item destination')
parser_move.add_argument('filter', choices=items.getItemCategories().keys(), nargs='+', help='Item filter')
parser_move.set_defaults(func=items.move)

parser_move = subparsers.add_parser('missing', help='Show missing items that are for sale')
parser_move.add_argument('collection', choices=['all','emblems','shaders','vehicles','ships'], help='Collection')
parser_move.set_defaults(func=vendor.missing)

args = parser.parse_args()

print 'Authenticating with PSN/Bungie...'

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

# Populate runtime config with common requirements to speed things up
print 'Fetching user information...'

config.session = session
if hasattr(config, 'USER_ID') and config.USER_ID != '':
	config.userId = config.USER_ID
else:
	config.userId = user.getId(config)
config.characters = user.getCharacters(config)

# Authentication is complete, time to do some work
args.func(config, args)

print 'Done.'
