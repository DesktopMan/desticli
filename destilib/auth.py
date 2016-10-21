# PSN + Bungie authentication
# From https://gist.github.com/ascendancyy/702db99b626d52d69359

import logging

from base64 import b64encode
from urlparse import urlparse

import httplib
httplib.HTTPConnection.debuglevel = 0

import requests
# https://urllib3.readthedocs.org/en/latest/security.html#insecurerequestwarning
requests.packages.urllib3.disable_warnings()

def login(username, password, api_key):
	logger = logging.getLogger(__name__)

	BUNGIE_SIGNIN_URI = "https://www.bungie.net/en/User/SignIn/Psnid"
	PSN_OAUTH_URI = "https://auth.api.sonyentertainmentnetwork.com/login.do"

	logger.info("Logging in...")

	# Get JSESSIONID cookie.
	# We follow the redirection just in case the URI ever changes.
	get_jessionid = requests.get(BUNGIE_SIGNIN_URI, allow_redirects=True)
	jsessionid0 = get_jessionid.history[1].cookies["JSESSIONID"]
	logger.debug("JSESSIONID: %s", jsessionid0)

	# The POST request will fail if the field `params` isn't present
	# in the body of the request.
	# The value is just the query string of the PSN login page
	# encoded in base64.
	params = urlparse(get_jessionid.url).query
	logger.debug("params: %s", params)
	params64 = b64encode(params)
	logger.debug("params64: %s", params64)

	# Post credentials and pass the JSESSIONID cookie.
	# We get a new JSESSIONID cookie.
	# Note: It doesn't appear to matter what the value of `params` is, but
	# we'll pass in the appropriate value just to be safe.
	post = requests.post(
		PSN_OAUTH_URI,
		data={"j_username": username, "j_password": password, "params": params64},
		cookies={"JSESSIONID": jsessionid0},
		params={"redirect_uri": BUNGIE_SIGNIN_URI},
		allow_redirects=False
	)
	if "authentication_error" in post.headers["location"]:
		logger.warning("Invalid credentials")
		return None

	jsessionid1 = post.cookies["JSESSIONID"]
	logger.debug("JSESSIONID: %s", jsessionid1)

	session = requests.Session()

	# Follow the redirect from the previous request passing in the new
	# JSESSIONID cookie. This gets us the Bungie cookies.
	session.get(
		post.headers["location"],
		allow_redirects=True,
		cookies={"JSESSIONID": jsessionid1}
	)

	# Add the API key to the current session
	session.headers["X-API-Key"] = api_key

	return session
