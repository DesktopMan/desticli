import collections
import json
import time

import user

def getItemCategories():
	ic = collections.OrderedDict()

	ic['all'] = []

	# Ascendant Shard, Ascendant Energy, Radiant Shard, Radiant Energy, Hadium Flake
	ic['materials'] = [ 258181985, 1893498008, 769865458, 616706469, 3164836593 ]

	# Spinmetal, Helium Filaments, Relic Iron, Spirit Bloom, Wormspore
	ic['resources'] = [ 2882093969, 1797491610, 3242866270, 2254123540, 3164836592 ]

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
		3164836593 : 'Hadium Flake',

		2882093969 : 'Spinmetal',
		1797491610 : 'Helium Filaments',
		3242866270 : 'Relic Iron',
		2254123540 : 'Spirit Bloom',
		3164836592 : 'Wormspore',

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

def getItemIds(categories):
	ic = getItemCategories()
	itemIds = []

	if 'all' in categories:
		for cat in ic:
			itemIds.extend(ic[cat])
	else:
		for cat in categories:
			itemIds.extend(ic[cat])

	return itemIds

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

def normalize(config, args):
	print 'Normalizing items...'

	itemIds = getItemIds(args.filter)
	inventories = user.getCharacterInventories(config)

	for itemId in itemIds:
		normalizeItem(config, itemId, inventories)

def normalizeItem(config, itemId, inventories):
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
						moveItem(config, itemId, c2, c, need)
						break
					else: # Not enough, move what we can and try the next inventory
						moveItem(config, itemId, c2, c, spare)
						need -= spare

def move(config, args):
	print 'Moving items...'

	itemIds = getItemIds(args.filter)
	inventories = user.getCharacterInventories(config)

	for itemId in itemIds:
		for character, items in inventories.iteritems():
			stackSize = getItemField(items, itemId, 'stackSize', 0)

			if stackSize > 0:
				moveItemToFromVault(config, itemId, character, stackSize, True)

def moveItem(config, itemId, source, dest, count):
	# First move the item(s) to the vault
	moveItemToFromVault(config, itemId, source, count, True)

	# Then move the item(s) to the destination
	moveItemToFromVault(config, itemId, dest, count, False)

def moveItemToFromVault(config, itemId, character, count, toVault):
	print "Moving %s * %d %s the vault..." % (getItemName(itemId), count, 'to' if toVault else 'from')

	URL = 'https://www.bungie.net/Platform/Destiny/TransferItem/'
	body = {}

	body['characterId'] = character
	body['membershipType'] = 2
	body['itemReferenceHash'] = itemId
	body['stackSize'] = count
	body['transferToVault'] = toVault

	response = config.session.post(URL, data=json.dumps(body))

	if response.status_code != 200:
		print 'Failed to move item(s) %s the vault. Server error.' % ('to' if toVault else 'from')
		time.sleep(1)
		return

	if json.loads(response.text)['ErrorStatus'] != 'Success':
		print 'Failed to move item(s) %s the vault. Vault/character full?' % ('to' if toVault else 'from')
		time.sleep(1)
		return

	time.sleep(1)
