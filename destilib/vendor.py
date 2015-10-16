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
		242140165  : 'Lord Saladin',
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
			'vendorIds' : [ 134701236, 1410745145, 242140165 ]
		},

		'shaders' : {
			'typeNames' : [ 'Armor Shader' ],
			'kioskIds'  : [ 2420628997 ],
			'vendorIds' : [ 134701236, 1998812735, 1410745145, 242140165 ]
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

	ignoredItems = [
		1880070441, # Plasma Drive
		1880070443, # Void Drive
		1880070442, # Stealth Drive
		1880070440, # "Emerald Coil"
		2633085824, # Glass Needles
		211861343,  # Heavy Ammo Synthesis
		417308266,  # Three of Coins
		937555249   # Mote of Light
	]

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
			print 'Unable to fetch vendor inventory. %s not available?' % (getVendorName(vendorId))
			continue

		saleItems = []
		for cat in vendor['saleItemCategories']:
			saleItems.extend(cat['saleItems'])

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

	response = json.loads(response.text)

	# Not all vendors are available at all times
	if response['ErrorStatus'] == 'DestinyVendorNotFound':
		return None, None

	if response['ErrorStatus'] != 'Success':
		print 'Failed to fetch vendor inventory. Request error?'
		return None, None

	data = response['Response']['data']

	if definitions:
		return data, response['Response']['definitions']

	return data, None
