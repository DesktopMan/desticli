import requests
import json

import user
import vendor

def update(config, args):
	URL = 'https://destinyexotics.com'

	username = config.EXOTICS_USERNAME
	password = config.EXOTICS_PASSWORD

	while not username:
		username = raw_input("Enter Destiny Exotics username: ")
	while not password:
	   password = getpass.getpass("Enter Destiny Exotics password: ")

	print 'Authenticating with Destiny Exotics...'

	session = requests.Session()

	body = {}

	body['username'] = username
	body['password'] = password

	response = session.post(URL + '/login', data=body)

	if response.status_code != 200:
		print 'Failed logging in to Destiny Exotics. Server error?'
		return

	response = json.loads(response.text)

	if response['status'] != 'ok':
		print 'Failed logging in to Destiny Exotics. Wrong username/password?'
		return

	userId = response['link'].split('/')[2]

	print 'Fetching item list from Destiny Exotics...'

	response = session.get(URL + '/api/items/?fields=itemHash&sections=true&user=%s' % (userId))

	if response.status_code != 200:
		print 'Failed fetching item list from Destiny Exotics. Server error?'
		return

	response = json.loads(response.text)

	if response['status'] != 'ok':
		print 'Failed fetching item list from Destiny Exotics. Bad request?'
		return

	items = {}

	# Initialize item list from Destiny Exotics
	for section in response['sections']:
		for group in section['groups']:
			for item in group['items']:
				items[int(item['itemHash'])] = 0

	print 'Fetching kiosk and character inventories...'

	# Check vendor kiosks first
	for character in config.characters:
		for kioskId in [1460182514, 3902439767]:
			collection = vendor.getVendorForCharacter(config, character, kioskId)[0]

			if not collection:
				print 'Failed to get collection content. Aborting.'
				return

			for cat in collection['saleItemCategories']:
				for item in cat['saleItems']:
					if item['failureIndexes'] != []:
						items[item['item']['itemHash']] = 0 # Not unlocked
					else:
						items[item['item']['itemHash']] = 1 # Unlocked

	# Then check current character inventories
	for character in config.characters:
		inventory = user.getCharacterInventory(config, character, 'Equippable')

		if not inventory:
			print 'Failed to get character inventory. Aborting.'
			return

		for item in inventory:
			itemHash = item['itemHash']
			if itemHash in items:
				if item['isGridComplete']:
					items[itemHash] = 2 # Fully upgraded
				elif items[itemHash] == 0:
					items[itemHash] = 1 # Not upgraded

	# Finally check the vault
	vault = user.getVaultInventory(config, 1)

	if not vault:
		print 'Failed to get vault inventory. Aborting.'
		return

	for item in vault:
		itemHash = item['itemHash']
		if itemHash in items:
			if item['isGridComplete']:
				items[itemHash] = 2 # Fully upgraded
			elif items[itemHash] == 0:
				items[itemHash] = 1 # Not upgraded

	print 'Updating Destiny Exotics...'

	body = {}
	body['items'] = []

	for itemHash, itemStatus in items.iteritems():
		body['items'].append({'itemHash': str(itemHash), 'visible': True, 'collected': itemStatus})

	response = session.post(URL + '/api/users/user/%s/items/' % (userId), data=json.dumps(body))
