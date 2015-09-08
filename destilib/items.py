import collections
import json
import time

import user

def getItemCategories():
	ic = collections.OrderedDict()

	ic['all'] = []

	# Ascendant Shard, Ascendant Energy, Radiant Shard, Radiant Energy
	ic['materials'] = [ 258181985, 1893498008, 769865458, 616706469 ]

	# Spinmetal, Helium Filaments, Relic Iron, Spirit Bloom
	ic['resources'] = [ 2882093969, 1797491610, 3242866270, 2254123540 ]

	# Primary, Special, Heavy
	ic['synths'] = [ 2180254632, 928169143, 211861343 ]

	# Auto Rifle, Scout Rifle, Hand Cannon, Sniper Rifle, Shutgun, Fusion Rifle, Rocket Launcher, Machine Gun, Primary, Special, Heavy
	ic['telemetries'] = [ 4159731660, 323927027, 846470091, 927802664, 4141501356, 729893597, 3036931873, 1485751393, 705234570, 3371478409, 2929837733 ]

	# Fallen, Hive, Vex, Kabal
	ic['glimmer_boosters'] = [ 3783295803, 1043138475, 1772853454, 3446457162 ]

	ic['weapon_parts'] = [ 1898539128 ]
	ic['armor_materials'] = [ 1542293174 ]
	ic['strange_coins'] = [ 1738186005 ]
	ic['motes_of_light'] = [ 937555249 ]
	ic['exotic_shards'] = [ 452597397 ]

	return ic

def getItemName(itemId):
	items = {
		258181985  : 'Ascendant Shard',
		1893498008 : 'Ascendant Energy',
		769865458  : 'Radiant Shard',
		616706469  : 'Radiant Energy',

		2882093969 : 'Spinmetal',
		1797491610 : 'Helium Filaments',
		3242866270 : 'Relic Iron',
		2254123540 : 'Spirit Bloom',

		2180254632 : 'Primary Synth',
		928169143  : 'Special Synth',
		211861343  : 'Heavy Synth',

		4159731660 : 'Auto Rifle Telemetry',
		323927027  : 'Scout Rifle Telemetry',
		846470091  : 'Hand Cannon Telemetry',
		927802664  : 'Sniper Rifle Telemetry',
		4141501356 : 'Shotgun Telemetry',
		729893597  : 'Fusion Rifle Telemetry',
		3036931873 : 'Rocket Launcher Telemetry',
		1485751393 : 'Machine Gun Telemetry',
		705234570  : 'Primary Telemetry',
		3371478409 : 'Special Telemetry',
		2929837733 : 'Heavy Telemetry',

		3783295803 : 'Ether Seeds',
		1043138475 : 'Black Wax Idol',
		1772853454 : 'Blue Polyphage',
		3446457162 : 'Resupply Codes',

		1898539128 : 'Weapon Parts',
		1542293174 : 'Armor Materials',
		1738186005 : 'Strange Coin',
		937555249  : 'Mote of Light',
		452597397  : 'Exotic Shard'
	}

	if itemId in items:
		return items[itemId]

	return 'Unknown Item'

def getItemField(inventory, itemId, field, default):
	# Special handling of stack size
	count = 0

	for item in inventory:
		if item['itemHash'] == itemId:
			if field != 'stackSize':
				return item[field]
			else:
				count += item[field]

	if field == 'stackSize':
		return count;

	return default

def normalize(config, session, args):
	ic = getItemCategories()
	itemIds = []

	if 'all' in args.filter:
		for cat in ic:
			itemIds.extend(ic[cat])
	else:
		for cat in args.filter:
			itemIds.extend(ic[cat])

	# Grab inventories, only done once per normalize
	userId = user.getId(session, config.DISPLAY_NAME)
	characters = user.getCharacters(session, userId)

	inventories = {}

	for c in characters:
		inventories[c] = getCharacterInventory(session, userId, c)

	for itemId in itemIds:
		normalizeItem(session, itemId, inventories)

def normalizeItem(session, itemId, inventories):
	# Fetch the stack size for each character
	itemCount = {}

	for c in inventories:
		itemCount[c] = getItemField(inventories[c], itemId, 'stackSize', 0)

	totalCount = sum(itemCount.values())

	# Can't normalize less than three items
	if totalCount < 3:
		return

	# Number of items we want per character
	targetCount = totalCount / len(inventories)

	for c in itemCount:
		if itemCount[c] < targetCount:
			need = targetCount - itemCount[c] # Needed items

			for c2 in inventories: # Look for spare items in the other inventories
				if itemCount[c2] > targetCount:
					spare = itemCount[c2] - targetCount

					if spare >= need: # Inventory has enough
						moveItem(session, itemId, c2, c, need)
						break
					else: # Not enough, move what we can and try the next inventory
						moveItem(session, itemId, c2, c, spare)
						need -= spare

def moveItem(session, itemId, source, dest, count):
	print "Moving %s * %d..." % (getItemName(itemId), count)

	URL = 'https://www.bungie.net/Platform/Destiny/TransferItem/'
	body = {}

	# First move the item(s) to the vault
	body['characterId'] = source
	body['membershipType'] = 2
	body['itemReferenceHash'] = itemId
	body['stackSize'] = count
	body['transferToVault'] = True

	response = session.post(URL, data=json.dumps(body))

	if response.status_code != 200:
		print 'Failed to move item(s) to the vault. Server error.'
		time.sleep(1)
		return

	if json.loads(response.text)['ErrorStatus'] != 'Success':
		print 'Failed to move item(s) to the vault. Vault full?'
		time.sleep(1)
		return

	time.sleep(1)

	# Then move the item(s) to the destination
	body['characterId'] = dest
	body['transferToVault'] = False

	response = session.post(URL, data=json.dumps(body))

	if response.status_code != 200:
		print 'Failed to move item(s) from the vault. Server error.'
		time.sleep(1)
		return

	if json.loads(response.text)['ErrorStatus'] != 'Success':
		print 'Failed to move item(s) from the vault. Character full?'
		time.sleep(1)
		return

	time.sleep(1)

def getCharacterInventory(session, userId, characterId):
	URL = 'https://www.bungie.net/Platform/Destiny/2/Account/%s/Character/%s/Inventory/?definitions=false'
	response = session.get(URL % (userId, characterId))
	itemData = json.loads(response.text)['Response']['data']['buckets']['Item']

	items = []

	for itemList in itemData:
		items.extend(itemList['items'])

	return items

def getVaultInventory(session):
	URL = 'https://www.bungie.net/Platform/Destiny/2/MyAccount/Vault/?definitions=false'

	response = session.get(URL)

	return json.loads(response.text)['Response']['data']['buckets'][2]['items']
