from . import xmlrpc
from . import helper

import logging

logger = logging.getLogger(__name__)

# Check if the session exists if not create one
def createSessionIfNotExists(request, response):
	# TODO test cookie
	# get sid if its not there
	sid = request.COOKIES.get('sessionId')
	if(sid is None):
		sid = xmlrpc.get_sid()
		# Send session id to the browser cookie
		helper.set_cookie(response, 'sessionId', sid)
		return False
	return True
