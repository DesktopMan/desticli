#!/usr/bin/python

import argparse

from destilib import items

api = "https://www.bungie.net/Platform/Destiny/"

parser = argparse.ArgumentParser(description='Destiny Command Line Interface')
subparsers = parser.add_subparsers(help='Choose sub-command')

parser_normalize = subparsers.add_parser('normalize', help='Normalize stacks evenly across characters')
parser_normalize.add_argument('filter', choices=items.getItemCategories().keys(), nargs='+', help='Item filter')
parser_normalize.set_defaults(func=items.normalize)

args = parser.parse_args()
args.func(args.filter)


