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

	response = session.get(URL + '/api/items/?fields=itemHash,visible&sections=true&user=%s' % (userId))

	if response.status_code != 200:
		print 'Failed fetching item list from Destiny Exotics. Server error?'
		return

	response = json.loads(response.text)

	if response['status'] != 'ok':
		print 'Failed fetching item list from Destiny Exotics. Bad request?'
		return

	exoticsItems = {}

	# Initialize item list from Destiny Exotics
	for section in response['sections']:
		for group in section['groups']:
			for item in group['items']:
				exoticsItems[int(item['itemHash'])] = { 'collected': 0, 'visible': item['visible'] }

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
					itemHash = item['item']['itemHash']

					if itemHash != 3386109374 and itemHash in exoticsItems: # Missing Exotic Blueprint
						exoticsItems[itemHash]['collected'] = 1 # Not upgraded

	# All character and vault items
	ownedItems = []

	# Then check current character inventories
	for character in config.characters:
		inventory = user.getCharacterInventory(config, character, 'Equippable')

		if not inventory:
			print 'Failed to get character inventory. Aborting.'
			return

		ownedItems.extend(inventory)

	# Finally check the vault
	vault = user.getVaultInventory(config, 1)

	if not vault:
		print 'Failed to get vault inventory. Aborting.'
		return

	ownedItems.extend(vault)

	for item in ownedItems:
		itemHash = item['itemHash']
		if itemHash in exoticsItems:
			if item['isGridComplete']:
				exoticsItems[itemHash]['collected'] = 2 # Fully upgraded
			elif exoticsItems[itemHash]['collected'] == 0:
				exoticsItems[itemHash]['collected'] = 1 # Not upgraded

	print 'Updating Destiny Exotics...'

	body = {}
	body['items'] = []

	for itemHash, item in exoticsItems.iteritems():
		body['items'].append({'itemHash': str(itemHash), 'visible': item['visible'], 'collected': item['collected']})

	response = session.post(URL + '/api/users/user/%s/items/' % (userId), data=json.dumps(body))
