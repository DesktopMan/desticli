import urlparse
import requests
import json

def getId(config):
	URL = 'https://www.bungie.net/Platform/Destiny/2/Stats/GetMembershipIdByDisplayName/'
	response = config.session.get(urlparse.urljoin(URL, config.DISPLAY_NAME))

	return json.loads(response.text)['Response']

def getCharacters(config):
	URL = 'https://www.bungie.net/Platform/Destiny/TigerPSN/Account/'
	response = config.session.get(urlparse.urljoin(URL, config.userId))

	data = json.loads(response.text)['Response']['data']

	characters = []

	for c in data['characters']:
		characters.append(c['characterBase']['characterId'])

	return characters

def getCharacterInventory(config, characterId, bucket = 'Item'):
	URL = 'https://www.bungie.net/Platform/Destiny/2/Account/%s/Character/%s/Inventory/?definitions=false'
	response = config.session.get(URL % (config.userId, characterId))

	itemData = json.loads(response.text)['Response']['data']['buckets'][bucket]

	items = []

	for itemList in itemData:
		items.extend(itemList['items'])

	return items

def getCharacterInventories(config):
	inventories = []

	for c in config.characters:
		inventories.append(getCharacterInventory(config, c))

	return inventories

def getVaultInventory(config, bucket = 2):
	URL = 'https://www.bungie.net/Platform/Destiny/2/MyAccount/Vault/?definitions=false'

	response = config.session.get(URL)

	return json.loads(response.text)['Response']['data']['buckets'][bucket]['items']
