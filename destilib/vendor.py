import json
import time

import config
import user

def missing(config, session, args):
	userId = user.getId(session, config.DISPLAY_NAME)
	characters = user.getCharacters(session, userId)

	if args.collection == 'emblems':
		getMissingEmblems(session, userId, characters)

def getMissingEmblems(session, userId, characters):
	print 'Looking for missing Emblems for sale...'

	# Grab the collection
	collection = getEmblemCollectionIventory(session, userId, characters[0], False)[0]
	if not collection:
		return

	# Find the collection Emblem vendor category
	haveItems = None
	for category in collection['saleItemCategories']:
		if category['categoryTitle'] == 'Vendor':
			haveItems = category['saleItems']
			break

	# Grab the outfitter inventory with definitions
	outfitter, definitions = getOutfitterInventory(session, userId, characters[0], True)
	if not outfitter:
		return

	# Find the outfitter Emblem category
	saleItems = None
	for category in outfitter['saleItemCategories']:
		if category['categoryTitle'] == 'Emblems':
			saleItems = category['saleItems']
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
			print "Missing Emblem for sale: %s" % (definitions['items'][str(itemId)]['itemName'])

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

def getOutfitterInventory(session, userId, character, definitions = False):
	return getVendorForCharacter(session, userId, character, 134701236, definitions)

def getEmblemCollectionIventory(session, userId, character, definitions = False):
	return getVendorForCharacter(session, userId, character, 3301500998, definitions)
