import json
import time

import config
import user

def missing(config, args):


	if 'all' in args.collection:
		args.collection = [ 'emblems', 'shaders', 'vehicles', 'ships' ]

	for group in args.collection:
		getMissingItems(config, group)

def getMissingItems(config, group):
	groupMapping = {
		'emblems' : { 'category': 'Emblems',         'kioskId': 3301500998, 'vendorId': 134701236 },
		'shaders' : { 'category': 'Shaders',         'kioskId': 2420628997, 'vendorId': 134701236 },
		'vehicles': { 'category': 'Vehicles',        'kioskId': 44395194,   'vendorId': 459708109 },
		'ships'   : { 'category': 'Ship Blueprints', 'kioskId': 2244880194, 'vendorId': 459708109 }
	}

	category = groupMapping[group]['category']
	kioskId  = groupMapping[group]['kioskId']
	vendorId = groupMapping[group]['vendorId']

	print 'Looking for missing %s for sale...' % (category)

	# Grab the collection
	collection = getVendorForCharacter(config, config.characters[0], kioskId)[0]
	if not collection:
		return

	# Find the collection items
	haveItems = []
	for cat in collection['saleItemCategories']:
		haveItems.extend(cat['saleItems'])

	# Grab the vendor inventory with definitions
	vendor, definitions = getVendorForCharacter(config, config.characters[0], vendorId, True)
	if not vendor:
		return

	# Find the vendor items
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

		if not owned:
			print "Missing: %s" % (definitions['items'][str(itemId)]['itemName'])

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
