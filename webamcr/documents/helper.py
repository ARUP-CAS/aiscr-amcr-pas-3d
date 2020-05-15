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


def load_project_cache(user_sid=None):
	if not user_sid:
		user_sid = xmlrpc.get_sid()
	TMP = []
	# TODO REFACTOR THIS
	try:
		TEMP_HLEDEJ_PROJECT3 = xmlrpc.hledej_projekt(user_sid, {
			'druh_vyzkumu': '3',
			'navrzene_k_archivaci': '',
			'stav': '3'})
		TEMP_HLEDEJ_PROJECT4 = xmlrpc.hledej_projekt(user_sid, {
			'druh_vyzkumu': '3',
			'navrzene_k_archivaci': '',
			'stav': '4'})
		TEMP_HLEDEJ_PROJECT = TEMP_HLEDEJ_PROJECT3 + TEMP_HLEDEJ_PROJECT4

		TEMP_PROJECT_ID = []
		for item in TEMP_HLEDEJ_PROJECT:
			TEMP_PROJECT_ID.append(item['id'])

		TEMP_PROJ_INFO = xmlrpc.nacti_informace_list(user_sid, 'projekt', TEMP_PROJECT_ID)

		PROJECT_CACHE = []
		for item in TEMP_PROJ_INFO:
			PROJECT_CACHE.append((item['0']['id'], item['0']['id_cj'], item['0']['odpovedny_pracovnik_zapisu']))
		if len(PROJECT_CACHE) > 1:
			c.PROJECTS_CACHE = PROJECT_CACHE
		TMP = PROJECT_CACHE
	except:
		TMP = c.PROJECTS_CACHE
	return TMP


def load_user_cache(user_sid=None):
	if not user_sid:
		user_sid = xmlrpc.get_sid()
	TMP = []
	try:
		TMP = xmlrpc.get_list(user_sid, 'uzivatele', 'prijmeni', 'jmeno')
		if len(TMP) > 1:
			c.USERS_CACHE = TMP
	except:
		TMP = c.USERS_CACHE
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


def one_time_load_cached_data():
	if len(c.USERS_CACHE) == 0:
		try:
			c.USERS_CACHE = load_user_cache()
		except:
			print("chyba: c.USERS_CACHE")
		try:
			c.PROJECTS_CACHE = load_project_cache()
		except:
			print("chyba: c.PROJECTS_CACHE")


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
	one_time_load_cached_data()
	# LOAD STATIC DATA
	# WHOLE THINGS
	c.SERIES_CACHE = xmlrpc.get_list(sid, c.SERIES, 'caption', 'vysvetlivka')
	c.EVENT_TYPE_CACHE = xmlrpc.get_list(sid, c.EVENT_TYPE)  # dynamic
	c.ORGANIZATIONS_CACHE = xmlrpc.get_list(sid, c.ORGANIZATIONS, 'nazev_zkraceny')  # dynamic
	c.ORGANIZATIONS_CACHE.sort(key=lambda tup: locale.strxfrm(tup[1]))
	c.ORGANIZATIONS_CACHE_DICT = dict(c.ORGANIZATIONS_CACHE)
	c.ACCESSIBILITY_CACHE = xmlrpc.get_list(sid, c.ACCESSIBILITY, 'caption', 'vyznam')  # ???
	c.PRESERVATION_CACHE = xmlrpc.get_list(sid, c.PRESERVATION, 'caption', 'vysvetlivka')  # dynamic
	c.CADASTRE_1_CACHE = xmlrpc.get_list(sid, c.CADASTRE_1, 'caption')  # constant
	c.CADASTRE_2_CACHE = xmlrpc.get_list(sid, c.CADASTRE_2, 'caption')  # constant
	c.CADASTRE_12_CACHE = c.CADASTRE_1_CACHE + c.CADASTRE_2_CACHE
	c.CADASTRY_DICT = dict(c.CADASTRE_12_CACHE)
	# c.COORDINATE_SYSTEM_CACHE = xmlrpc.get_list(sid, c.COORDINATE_SYSTEM,'nazev')
	c.DISTRICTS_CACHE = xmlrpc.get_list(sid, c.DISTRICTS, 'caption', 'full_name')  # okresy??
	c.REGIONS_CACHE = xmlrpc.get_list(sid, c.REGIONS, 'caption')  # kraje??
	c.COUNTRIES_CACHE = xmlrpc.get_list(sid, c.COUNTRY)  # ??
	c.OBJECT_SPECIFICATION_CACHE = xmlrpc.get_list(sid, c.OBJECT_SPECIFICATION, 'nazev')  # dynamic
	c.OBJECT_TYPE_CACHE = xmlrpc.get_list(sid, c.OBJECT_TYPE, 'nazev')  # constant
	c.CIRCUMSTANCE_CACHE = xmlrpc.get_list(sid, c.CIRCUMSTANCE, 'nazev', poradi=True)  # dynamic
	# Periods grouped dropdown
	c.PERIOD_12_CACHE = groupedBox(
		c.PERIOD_FIRST, ['poradi', 'nazev'], c.PERIOD_SECOND, ['poradi', 'prvni', 'nazev'])  # dynamic
	c.PERIOD_2_CACHE = xmlrpc.get_list(sid, c.PERIOD_SECOND, 'nazev')  # dynamic
	c.PERIOD_12_CACHE_DICT = dict(c.PERIOD_12_CACHE)

	# predmet druh grouped drowdown
	c.PREDMET_KIND_CACHE = groupedBox(
		c.PREDMET_KIND1, ['poradi', 'nazev'], c.PREDMET_KIND2, ['poradi', 'prvni', 'nazev'])  # dynamic
	c.PREDMET_KIND2_CACHE = xmlrpc.get_list(sid, c.PREDMET_KIND2, 'nazev')  # dynamic
	# objekt druh grouped dropdown
	c.OBJEKT_KIND_12_CACHE = groupedBox(
		c.OBJEKT_KIND1, ['poradi', 'nazev'], c.OBJEKT_KIND2, ['poradi', 'prvni', 'nazev'])

	# object areal
	c.AREAL_12_CACHE = groupedBox(
		c.AREAL_FIRST, ['poradi', 'nazev'], c.AREAL_SECOND, ['poradi', 'prvni', 'nazev'])
	c.AREAL_12_CACHE_DICT = dict(c.AREAL_12_CACHE)

	# object specification
	c.SPECIFICATION_12_CACHE = groupedBox(
		c.SPECIFICATION_FIRST, ['poradi', 'nazev'], c.SPECIFICATION_SECOND, ['poradi', 'prvni', 'nazev'])

	# SUBSETS
	c.FORMAT_CACHE = xmlrpc.get_list_3D_model_type_form(sid, c.FORMAT)  # dynamic
	c.DOCUMENT_TYPE_CACHE = xmlrpc.get_list_3D_model_type_form(sid, c.DOCUMENT_TYPE)  # constant


# Function to dump c from heslare to file
def dump_cached_data_to_file():
	print('Dumping constants to file constants.pkl')
	f1 = open('constants.pkl', 'wb')

	# Load from the XMLRPC
	# Documents
	one_time_load_cached_data_doc()
	constants_file_struct = {
		# Documents
		'SERIES_CACHE': c.SERIES_CACHE,
		'EVENT_TYPE_CACHE': c.EVENT_TYPE_CACHE,
		'ORGANIZATIONS_CACHE': c.ORGANIZATIONS_CACHE,
		'ACCESSIBILITY_CACHE': c.ACCESSIBILITY_CACHE,
		'PRESERVATION_CACHE': c.PRESERVATION_CACHE,
		'CADASTRE_1_CACHE': c.CADASTRE_1_CACHE,
		'CADASTRE_2_CACHE': c.CADASTRE_2_CACHE,
		'CADASTRE_12_CACHE': c.CADASTRE_12_CACHE,
		'DISTRICTS_CACHE': c.DISTRICTS_CACHE,
		'REGIONS_CACHE': c.REGIONS_CACHE,
		'COUNTRIES_CACHE': c.COUNTRIES_CACHE,
		'OBJECT_SPECIFICATION_CACHE': c.OBJECT_SPECIFICATION_CACHE,
		'OBJECT_TYPE_CACHE': c.OBJECT_TYPE_CACHE,
		'CIRCUMSTANCE_CACHE': c.CIRCUMSTANCE_CACHE,
		'PERIOD_12_CACHE': c.PERIOD_12_CACHE,
		'PERIOD_2_CACHE': c.PERIOD_2_CACHE,
		'PREDMET_KIND_CACHE': c.PREDMET_KIND_CACHE,
		'PREDMET_KIND2_CACHE': c.PREDMET_KIND2_CACHE,
		'FORMAT_CACHE': c.FORMAT_CACHE,
		'DOCUMENT_TYPE_CACHE': c.DOCUMENT_TYPE_CACHE,
		'AREAL_12_CACHE': c.AREAL_12_CACHE,
		'OBJEKT_KIND_12_CACHE': c.OBJEKT_KIND_12_CACHE,
		'SPECIFICATION_12_CACHE': c.SPECIFICATION_12_CACHE,
		# Detectors
		'USERS_CACHE': c.USERS_CACHE,
		'PROJECTS_CACHE': c.PROJECTS_CACHE,
	}

	pickle.dump(constants_file_struct, f1)
	f1.close()


# Function to load constants from file rather then from php server
def load_cached_data_from_file():
	print('Loading constants from file')

	file_path = os.path.join(settings.BASE_DIR, 'constants.pkl')
	print(file_path)
	file2 = open(file_path, 'rb')
	cosntants_data = pickle.load(file2)

	# Documents
	c.SERIES_CACHE = cosntants_data.get('SERIES_CACHE')
	c.EVENT_TYPE_CACHE = cosntants_data.get('EVENT_TYPE_CACHE')
	c.ORGANIZATIONS_CACHE = cosntants_data.get('ORGANIZATIONS_CACHE')
	c.ORGANIZATIONS_CACHE.sort(key=lambda tup: locale.strxfrm(tup[1]))
	c.ACCESSIBILITY_CACHE = cosntants_data.get('ACCESSIBILITY_CACHE')
	c.PRESERVATION_CACHE = cosntants_data.get('PRESERVATION_CACHE')
	c.CADASTRE_1_CACHE = cosntants_data.get('CADASTRE_1_CACHE')
	c.CADASTRE_2_CACHE = cosntants_data.get('CADASTRE_2_CACHE')
	c.CADASTRE_12_CACHE = cosntants_data.get('CADASTRE_12_CACHE')
	c.DISTRICTS_CACHE = cosntants_data.get('DISTRICTS_CACHE')
	c.REGIONS_CACHE = cosntants_data.get('REGIONS_CACHE')
	c.COUNTRIES_CACHE = cosntants_data.get('COUNTRIES_CACHE')
	c.OBJECT_SPECIFICATION_CACHE = cosntants_data.get('OBJECT_SPECIFICATION_CACHE')
	c.OBJECT_TYPE_CACHE = cosntants_data.get('OBJECT_TYPE_CACHE')
	c.CIRCUMSTANCE_CACHE = cosntants_data.get('CIRCUMSTANCE_CACHE')
	c.PERIOD_12_CACHE = cosntants_data.get('PERIOD_12_CACHE')
	c.PERIOD_2_CACHE = cosntants_data.get('PERIOD_2_CACHE')
	c.PREDMET_KIND_CACHE = cosntants_data.get('PREDMET_KIND_CACHE')
	c.PREDMET_KIND2_CACHE = cosntants_data.get('PREDMET_KIND2_CACHE')
	c.FORMAT_CACHE = cosntants_data.get('FORMAT_CACHE')
	c.DOCUMENT_TYPE_CACHE = cosntants_data.get('DOCUMENT_TYPE_CACHE')
	c.AREAL_12_CACHE = cosntants_data.get('AREAL_12_CACHE')
	c.OBJEKT_KIND_12_CACHE = cosntants_data.get('OBJEKT_KIND_12_CACHE')
	c.SPECIFICATION_12_CACHE = cosntants_data.get('SPECIFICATION_12_CACHE')

	# Detectors
	c.USERS_CACHE = cosntants_data.get('USERS_CACHE')
	c.PROJECTS_CACHE = cosntants_data.get('PROJECTS_CACHE')

	# ----Dictionaries ----
	c.AREAL_12_CACHE_DICT = dict(c.AREAL_12_CACHE)
	c.ORGANIZATIONS_CACHE_DICT = dict(c.ORGANIZATIONS_CACHE)
	c.PERIOD_12_CACHE_DICT = dict(c.PERIOD_12_CACHE)
	c.CADASTRY_DICT = dict(c.CADASTRE_12_CACHE)

	file2.close()


def calculateCrc32(file):
	prev = 0
	for eachLine in file:
		prev = zlib.crc32(eachLine, prev)
	checksum = "%d" % (prev & 0xFFFFFFFF)
	return checksum


def bool_to_str(value):
	if (value):
		return 'Ano'
	else:
		return 'Ne'


def date_to_psql_date(dws):

	if dws.find("..") is not -1:
		return '-1'
	else:
		return "{}-{}-{}".format(dws[6:10], dws[3:5], dws[0:2])


def date_from_psql_date(dws):

	if dws.find("..") is not -1:
		return '-1'
	else:
		return "{}/{}/{}".format(dws[8:10], dws[5:7], dws[0:4])


def groupedBox(name1, arr1, name2, arr2):
	sid = xmlrpc.get_sid()
	kind1 = xmlrpc.get_list_columns(sid, name1, arr1)
	kind2 = xmlrpc.get_list_columns(sid, name2, arr2)
	kind1.sort()
	kind2.sort()
	myArr = []
	for p1 in kind1:
		opt_key = p1[2]
		opt_list = []
		for p2 in kind2:
			if p2[2] == p1[0]:
				opt_list.append((p2[0], p2[3]))
		# logger.debug((opt_key,tuple(opt_list)))
		myArr.append((opt_key, tuple(opt_list)))
	return myArr
