import json
import time

import config
import user

def missing(config, session, args):
	category = ''
	kioskId = None
	vendorId = None

	if args.collection == 'all':
		args.collection = 'emblems'
		missing(config, session, args)
		args.collection = 'shaders'
		missing(config, session, args)
		args.collection = 'vehicles'
		missing(config, session, args)
		args.collection = 'ships'
		missing(config, session, args)
		return

	if args.collection == 'emblems':
		category = 'Emblems'
		kioskId = 3301500998
		vendorId = 134701236

	if args.collection == 'shaders':
		category = 'Shaders'
		kioskId = 2420628997
		vendorId = 134701236

	if args.collection == 'vehicles':
		category = 'Vehicles'
		kioskId = 44395194
		vendorId = 459708109

	if args.collection == 'ships':
		category = 'Ship Blueprints'
		kioskId = 2244880194
		vendorId = 459708109

	userId = user.getId(session, config.DISPLAY_NAME)
	characters = user.getCharacters(session, userId)

	print 'Looking for missing %s for sale...' % (category)

	# Grab the collection
	collection = getVendorForCharacter(session, userId, characters[0], kioskId, False)[0]
	if not collection:
		return

	# Find the collection items
	haveItems = []
	for cat in collection['saleItemCategories']:
		haveItems.extend(cat['saleItems'])

	# Grab the vendor inventory with definitions
	vendor, definitions = getVendorForCharacter(session, userId, characters[0], vendorId, True)
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

def getVendorForCharacter(session, userId, character, vendor, definitions = False):
	URL = 'https://www.bungie.net/Platform/Destiny/2/MyAccount/Character/%s/Vendor/%i/?definitions=%s' % (character, vendor, 'true' if definitions else 'false')

	response = session.get(URL)
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
