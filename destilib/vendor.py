import json
import time

import config
import user

def getVendorName(vendorId):
	vendors = {
		2668878854 : 'Vanguard Quartermaster',
		3658200622 : 'Crucible Quartermaster',
		459708109  : 'Shipwright',
		134701236  : 'Guardian Outfitter',
		1998812735 : 'Variks',
		1410745145 : 'Petra',
		2796397637 : 'Xur'
	}

	if vendorId in vendors:
		return vendors[vendorId]

	return 'Unknown Vendor'

def missing(config, args):
	if 'all' in args.collection:
		args.collection = [ 'emblems', 'shaders', 'vehicles', 'ships', 'exotics' ]

	for group in args.collection:
		getMissingItems(config, group)

def getMissingItems(config, group):
	groupMapping = {
		'emblems' : {
			'typeNames' : [ 'Emblem' ],
			'kioskIds'  : [ 3301500998 ],
			'vendorIds' : [ 134701236, 1410745145 ]
		},

		'shaders' : {
			'typeNames' : [ 'Armor Shader' ],
			'kioskIds'  : [ 2420628997 ],
			'vendorIds' : [ 134701236, 1998812735, 1410745145 ]
		},

		'vehicles': {
			'typeNames' : [ 'Vehicle'] ,
			'kioskIds'  : [ 44395194   ],
			'vendorIds' : [ 2668878854, 3658200622, 459708109 ]
		},

		'ships'   : {
			'typeNames' : [ 'Ship' ],
			'kioskIds'  : [ 2244880194 ],
			'vendorIds' : [ 459708109, 1998812735, 1410745145 ]
		},

		'exotics' : {
			'typeNames' : [], # All types
			'kioskIds'  : [ 1460182514, 3902439767 ],
			'vendorIds' : [ 2796397637 ]
		}
	}

	# Plasma Drive, "Emerald Coil", Heavy Ammo Synthesis, Three of Coins, Mote of Light
	ignoredItems = [ 1880070441, 1880070440, 211861343, 417308266, 937555249 ]

	typeNames = groupMapping[group]['typeNames']
	kioskIds  = groupMapping[group]['kioskIds']
	vendorIds = groupMapping[group]['vendorIds']

	print
	print 'Looking for missing %s...' % (group)

	# Grab the collection
	haveItems = []

	for kioskId in kioskIds:
		collection = []

		characters = []
		# The exotic armor kiosk has different inventories for different classes
		if group == 'exotics':
			characters = config.characters
		else:
			characters = [ config.characters[0] ]

		for character in characters:
			collection = getVendorForCharacter(config, character, kioskId)[0]

			if not collection:
				print 'Failed to get collection content. Aborting.'
				return

			for cat in collection['saleItemCategories']:
				haveItems.extend(cat['saleItems'])

	# Count the total number of collection items still missing
	totalMissing = 0

	for colItem in haveItems:
		if colItem['failureIndexes'] != []:
			totalMissing += 1

	print 'Collection is missing %i %s.' % (totalMissing, group if totalMissing != 1 else group[:-1])

	foundMissingItems = []

	# Check the vendor items for each vendor
	for vendorId in vendorIds:
		vendor, definitions = getVendorForCharacter(config, config.characters[0], vendorId, True)

		if not vendor:
			print 'Failed to get vendor content. Aborting.'
			return

		saleItems = []
		for cat in vendor['saleItemCategories']:
			saleItems.extend(cat['saleItems'])

		# Xur doesn't always have items
		if not saleItems and vendorId == 2796397637:
			print 'Found no Xur items for sale. Weekday?'
			continue

		if not saleItems:
			print 'Found no items for sale. API issue?'
			continue

		# Look for each item in our collection
		for saleItem in saleItems:
			itemHash = saleItem['item']['itemHash']
			typeName = definitions['items'][str(itemHash)]['itemTypeName']

			if typeNames and not typeName in typeNames:
				continue

			owned = False

			for colItem in haveItems:
				if colItem['item']['itemHash'] == itemHash and colItem['failureIndexes'] == []:
					owned = True
					break

			itemName = definitions['items'][str(itemHash)]['itemName']

			if not owned and not itemName.endswith('Engram') and not itemHash in ignoredItems:
				foundMissingItems.append({
					'itemHash': itemHash,
					'itemName': itemName,
					'rarity': definitions['items'][str(itemHash)]['tierTypeName'],
					'vendor': getVendorName(vendorId)
				})

	fmc = len(foundMissingItems) # Found missing count
	print 'Found %i missing %s for sale%s' % (fmc, group if fmc != 1 else group[:-1], ':' if fmc else '.')

	for item in foundMissingItems:
		print '* %s (%s, %s)' % (item['itemName'], item['rarity'], item['vendor'])

def getVendorForCharacter(config, characterId, vendorId, definitions = False):
	URL = 'https://www.bungie.net/Platform/Destiny/2/MyAccount/Character/%s/Vendor/%i/?definitions=%s' % (characterId, vendorId, 'true' if definitions else 'false')

	response = config.session.get(URL)
	time.sleep(1)

	if response.status_code != 200:
		print 'Failed to fetch vendor inventory. Server error.'
		return None, None

	if json.loads(response.text)['ErrorStatus'] != 'Success':
		print 'Failed to fetch vendor inventory. Request error?'
		return None, None

	response = json.loads(response.text)['Response']
	data = response['data']

	if definitions:
		return response['data'], response['definitions']

	return response['data'], None
