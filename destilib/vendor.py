import json
import time

import config
import user

def getVendorName(vendorId):
	vendors = {
		134701236  : 'Guardian Outfitter',
		459708109  : 'Shipwright',
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
		'emblems' : { 'category': 'Emblems',         'kioskIds': [ 3301500998 ], 'vendorIds': [ 134701236 ] },
		'shaders' : { 'category': 'Shaders',         'kioskIds': [ 2420628997 ], 'vendorIds': [ 134701236 ] },
		'vehicles': { 'category': 'Vehicles',        'kioskIds': [ 44395194   ], 'vendorIds': [ 459708109 ] },
		'ships'   : { 'category': 'Ship Blueprints', 'kioskIds': [ 2244880194 ], 'vendorIds': [ 459708109 ] },
		'exotics' : { 'category': 'Exotic Gear',     'kioskIds': [ 1460182514, 3902439767 ], 'vendorIds': [ 2796397637 ] }
	}

	category = groupMapping[group]['category']
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

		saleItems = None
		for cat in vendor['saleItemCategories']:
			if cat['categoryTitle'] == category:
				saleItems = cat['saleItems']
				break

		# Look for each item in our collection
		for saleItem in saleItems:
			itemId = saleItem['item']['itemHash']

			owned = False

			for colItem in haveItems:
				if colItem['item']['itemHash'] == itemId and colItem['failureIndexes'] == []:
					owned = True
					break

			itemName = definitions['items'][str(itemId)]['itemName']
			if not owned and not itemName.endswith('Engram'):
				foundMissingItems.append({ 'itemId': itemId, 'itemName': itemName, 'vendorId': vendorId })

	fmc = len(foundMissingItems) # Found missing count
	print 'Found %i missing %s for sale%s' % (fmc, group if fmc != 1 else group[:-1], ':' if fmc else '.')

	for item in foundMissingItems:
		print '* %s (%s)' % (item['itemName'], getVendorName(item['vendorId']))

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
