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
