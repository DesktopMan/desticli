import urlparse
import requests
import json

def getId(session, displayName):
	URL = 'https://www.bungie.net/Platform/Destiny/2/Stats/GetMembershipIdByDisplayName/'
	response = session.get(urlparse.urljoin(URL, displayName))

	return json.loads(response.text)['Response']

def getCharacters(session, id):
	URL = 'https://www.bungie.net/Platform/Destiny/TigerPSN/Account/'
	response = session.get(urlparse.urljoin(URL, id))

	data = json.loads(response.text)['Response']['data']

	characters = []

	for c in data['characters']:
		characters.append(c['characterBase']['characterId'])

	return characters

def getCharacterInventory(session, userId, characterId):
	URL = 'https://www.bungie.net/Platform/Destiny/2/Account/%s/Character/%s/Inventory/?definitions=false'
	response = session.get(URL % (userId, characterId))
	itemData = json.loads(response.text)['Response']['data']['buckets']['Item']

	items = []

	for itemList in itemData:
		items.extend(itemList['items'])

	return items

def getCharacterInventories(session, userId, characters):
	inventories = {}

	for c in characters:
		inventories[c] = getCharacterInventory(session, userId, c)

	return inventories

def getVaultInventory(session):
	URL = 'https://www.bungie.net/Platform/Destiny/2/MyAccount/Vault/?definitions=false'

	response = session.get(URL)

	return json.loads(response.text)['Response']['data']['buckets'][2]['items']
