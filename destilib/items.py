import collections

def getItemCategories():
	ic = collections.OrderedDict()

	ic['all'] = {}
	ic['materials'] = {}
	ic['resources'] = {}
	ic['weapon_parts'] = { 1898539128 }
	ic['ammunition'] = { 2180254632, 928169143, 211861343 }
	ic['telemetries'] = {}
	ic['strange_coins'] = { 1738186005 }
	ic['motes_of_light'] = { 937555249 }
	ic['glimmer_boosters'] = {}

	return ic

def normalize(categories):
	ic = getItemCategories()
	items = []

	if 'all' in categories:
		for cat in ic:
			items.extend(ic[cat])
	else:
		for cat in categories:
			items.extend(ic[cat])

	print items
