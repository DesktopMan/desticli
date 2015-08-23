#!/usr/bin/python

import argparse
import collections

api = "https://www.bungie.net/Platform/Destiny/"

def getItemCategories():
	ic = collections.OrderedDict()

	ic['all'] = {}
	ic['materials'] = {}
	ic['resources'] = {}
	ic['weapon_parts'] = { 1898539128 }
	ic['ammunition'] = { 2180254632, 928169143, 211861343 }
	ic['telemetries'] = {}
	ic['strange_coins'] = { 1738186005 }
	ic['motes_of_light'] = { 937555249 }
	ic['glimmer_boosters'] = {}

	return ic

def normalize(args):
	ic = getItemCategories()
	items = []

	if 'all' in args.filter:
		for cat in ic:
			items.extend(ic[cat])
	else:
		for cat in args.filter:
			items.extend(ic[cat])

	print items

parser = argparse.ArgumentParser(description='Destiny Command Line Interface')
subparsers = parser.add_subparsers(help='Choose sub-command')

parser_normalize = subparsers.add_parser('normalize', help='Normalize stacks evenly across characters')
parser_normalize.add_argument('filter', choices=getItemCategories().keys(), nargs='+', help='Item filter')
parser_normalize.set_defaults(func=normalize)

args = parser.parse_args()
args.func(args)


