import time
import zlib
import pickle
import logging
import os
import locale

from django.conf import settings
from .constants import AmcrConstants as c
from . import xmlrpc

logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')  # On server (Linux) 'Czech' locale is not avaliable, on windows it works


def load_user_cache(user_sid=None):
	if not user_sid:
		user_sid = xmlrpc.get_sid()
	TMP = []
	try:
		TMP = xmlrpc.get_list(user_sid, 'uzivatele', 'prijmeni', 'jmeno')
	except:
		logger.warning('Could not load users from xmlrpc server')
	return TMP


def load_name_cache(user_sid=None):
	if not user_sid:
		user_sid = xmlrpc.get_sid()
	TMP = []
	try:
		TMP = xmlrpc.get_list(user_sid, 'jmena', 'prijmeni', 'jmeno')
		if len(TMP) > 1:
			c.NAMES_CACHE = TMP
	except:
		TMP = c.NAMES_CACHE

	return TMP


def set_cookie(response, key, value, max_age_seconds=settings.AMCR_LOGIN_INT):
	response.set_cookie(
		key,
		value,
		max_age=max_age_seconds,
		domain=settings.SESSION_COOKIE_DOMAIN,
		secure=settings.SESSION_COOKIE_SECURE or None)


def parse_parameters(params):

	params_list = []

	if '&' in params:
		params_list = params.split('&')
	else:
		params_list.append(params)

	parameters = {}

	for p in params_list:
		if '=' in p:
			keyVal = p.split('=')
			parameters[keyVal[0]] = keyVal[1]
	return parameters


def create_parameters(params_dict):
	parameters = ''
	for p in params_dict:
		parameters = parameters + p + '=' + params_dict[p] + '&'
	return parameters


# Jméno uživ. skupiny    kód   kód binárně  Označení v hesláři Přístupnost
# anonym                  0     0                     A
# badatel                 1     1                     B
# archeolog               2     10                    C
# archivář                16    10000                 D
# administrátor           4     100                   E
# user admin              8                           Oprávnění (de)aktivovat uživatele
#  --------------- OPRAVNENI --------------
#  archivar detektoru     32
#  spravce uctu           64
#  spravce 3D             128
def get_roles_and_permissions(authLevel):

	authLevelResp = {
		'opravneni': [],
	}

	if((authLevel & 1) == 1):
		authLevelResp['role'] = c.BADATEL
	elif((authLevel & 2) == 2):
		authLevelResp['role'] = c.ARCHEOLOG
	elif((authLevel & 4) == 4):
		authLevelResp['role'] = c.ADMIN
	elif((authLevel & 16) == 16):
		authLevelResp['role'] = c.ARCHIVAR
	else:
		authLevelResp['role'] = c.NEAKTIVNI_UZIVATEL

	if((authLevel & 128) == 128):
		authLevelResp['opravneni'].append(c.ADMIN3D)
	if((authLevel & 64) == 64):
		authLevelResp['opravneni'].append(c.ACCOUNTS_ADMIN)
	# if((authLevel & 32) == 32):
	# 	authLevelResp['opravneni'].append(c.ARCHIVAR_DETECTORS)
	if((authLevel & 8) == 8):
		authLevelResp['opravneni'].append(c.USERS_ADMIN)

	return authLevelResp


def is_user_logged_in(request):

	sid = request.COOKIES.get('sessionId')

	if(sid is None):
		logger.debug("sid not found, retrieving new one from the php server")
		sid = xmlrpc.get_sid()
		return False, {}
	else:
		try:
			user = xmlrpc.get_current_user(sid)
			if(len(user) == 0):
				print("Sid " + str(sid) + " no longer valid on the php server.")
				return False, {}
			else:
				return True, user
		except:
			return False, {}


def min_user_group(user, minGroup):

	# Now check if the user group is ok
	userRolesPerm = get_roles_and_permissions(user['auth'])
	role = userRolesPerm['role']
	if minGroup == c.ADMIN:
		return role in c.USER_GROUP_SET_MIN_ADMIN
	elif minGroup == c.ARCHIVAR:
		return role in c.USER_GROUP_SET_MIN_ARCHIVAR
	elif minGroup == c.ARCHEOLOG:
		return role in c.USER_GROUP_SET_MIN_ARCHEOLOG
	elif minGroup == c.BADATEL:
		return role in c.USER_GROUP_SET_MIN_BADATEL
	elif minGroup == c.NEAKTIVNI_UZIVATEL:
		return role in c.USER_GROUP_SET_MIN_ANONYM
	else:
		return False


def check_user_group_and_permission(user, group_req, permission_req):
	logger.debug("Permission required: " + permission_req)
	userRolesPerm = get_roles_and_permissions(user['auth'])
	role = userRolesPerm['role']
	permissions = userRolesPerm['opravneni']
	logger.debug("Permissions of the user: " + str(permissions))
	if (group_req == role or group_req == '') and permission_req in permissions:
		return True
	return False


def get_logged_user_id(sid):

	user = xmlrpc.get_current_user(sid)
	if len(user) == 0:
		return 0
	else:
		return user['id']


def get_archeologist_id(sid, email):

	resp = xmlrpc.get_dict(sid, 'uzivatele')

	for user in resp:
		role = get_roles_and_permissions(user['auth'])['role']
		if role in ('Archeolog', 'Archivář', 'Admin') and (user['email'] == email):
			return user['id']

	return -1


# Map id of records in heslare to its textual description
# def map_id_to_description()
# Change time represenation
def current_timestamp():
	return int(time.mktime(time.localtime()))


def epoch_timestamp_to_datetime(epoch):

	if(epoch == 0 or epoch is None or epoch == ''):
		return 'N/A'

	return time.strftime('%Y-%m-%d %H:%M', time.localtime(epoch))


def getCurrentEpochTime():
	return str(int(time.time()))


# Function to load static data from the database at startup
def one_time_load_cached_data_doc():

	sid = xmlrpc.get_sid()

	print("Loading static data ....")
	# WHOLE THINGS
	c.CADASTRE_1_CACHE = xmlrpc.get_list(sid, c.CADASTRE_1, 'caption')  # constant
	c.CADASTRE_2_CACHE = xmlrpc.get_list(sid, c.CADASTRE_2, 'caption')  # constant
	c.CADASTRE_12_CACHE = c.CADASTRE_1_CACHE + c.CADASTRE_2_CACHE
	c.CADASTRY_DICT = dict(c.CADASTRE_12_CACHE)


# Function to dump c from heslare to file
def dump_cached_data_to_file():
	print('Dumping constants to file constants.pkl')
	f1 = open('constants.pkl', 'wb')

	# Load from the XMLRPC
	# Documents
	one_time_load_cached_data_doc()
	constants_file_struct = {
		# Documents
		'CADASTRE_1_CACHE': c.CADASTRE_1_CACHE,
		'CADASTRE_2_CACHE': c.CADASTRE_2_CACHE,
		'CADASTRE_12_CACHE': c.CADASTRE_12_CACHE,
	}

	pickle.dump(constants_file_struct, f1)
	f1.close()


# Function to load constants from file rather then from php server
def load_cached_data_from_file():
	print('Loading constants from file')

	file_path = os.path.join(settings.BASE_DIR, 'constants.pkl')
	file2 = open(file_path, 'rb')
	cosntants_data = pickle.load(file2)

	# Documents
	c.CADASTRE_1_CACHE = cosntants_data.get('CADASTRE_1_CACHE')
	c.CADASTRE_2_CACHE = cosntants_data.get('CADASTRE_2_CACHE')
	c.CADASTRE_12_CACHE = cosntants_data.get('CADASTRE_12_CACHE')

	# ----Dictionaries ----
	c.CADASTRY_DICT = dict(c.CADASTRE_12_CACHE)

	file2.close()


def calculateCrc32(file):
	prev = 0
	for eachLine in file:
		prev = zlib.crc32(eachLine, prev)
	checksum = "%d" % (prev & 0xFFFFFFFF)
	return checksum


def date_to_psql_date(dws):

	if dws.find("..") is not -1:
		return '-1'
	else:
		return "{}-{}-{}".format(dws[6:10], dws[3:5], dws[0:2])


def date_from_psql_date(dws):

	if not dws:
		return ''
	else:
		return "{}/{}/{}".format(dws[8:10], dws[5:7], dws[0:4])
