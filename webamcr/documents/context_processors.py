from django.conf import settings
from django.shortcuts import get_object_or_404

from .constants import AmcrConstants as constants
from . import helper, xmlrpc
from detectors.models import Organizace


def constants_import(request):

	constants_dict = {
		'AMCR_VERSION': constants.AMCR_VERSION,
		'MAIN_MENU': constants.MAIN_MENU,
		'LIBRARY_3D': constants.LIBRARY_3D,
		'MODULE_3D': constants.MODULE_3D,
		'CREATE_ENTRY': constants.CREATE,
		'MY_FINDS': constants.MY_FINDS,
		'MY_MODELS': constants.MY_MODELS,
		'CHOOSE_ENTRY': constants.CHOOSE,
		'UPLOAD': constants.UPLOAD,
		'MANAGE_DOC': constants.MANAGE_DOC,
		'MODUL_DETECTOR': constants.MODUL_DETECTORS,
		'COOP_DETECTOR': constants.COOP_DETECTOR,
		'CONFIRM_DETECTOR': constants.CONFIRM_DETECTOR,
		'ARCHIVE_DETECTOR': constants.ARCHIVE_DETECTOR,
		'SELECTED_FINDINGS': constants.SELECTED_FINDINGS,
		'USER_SETTINGS': constants.USER_SETTINGS,
		'HOME': constants.HOME,
		'AMCR_API': settings.AMCR_API,
		'DET_CARD_HEADER': constants.DET_CARD_HEADER,
		'DOC_CARD_HEADER': constants.DOC_CARD_HEADER,
		# Settings
		'AMCR_LOGIN_INT': settings.AMCR_LOGIN_INT,
		'DEBUG': settings.DEBUG,
		'INACTIVITY_INTERVAL': settings.INACTIVITY_INTERVAL,
		'INACTIVITY_NOTIF_INT': settings.INACTIVITY_NOTIF_INT
	}

	return constants_dict

def user_import(request):

	sid = request.COOKIES.get('sessionId')
	userDetail = {}

	if sid is not None:
		userInfo = xmlrpc.get_current_user(sid)
		if len(userInfo) != 0:
			fullName = userInfo['jmeno'] + ' ' + userInfo['prijmeni']
			# print('AuthLvl: ' + str(userInfo['auth']))
			user_id = int(userInfo['id'])
			role_opravneni = helper.get_roles_and_permissions(int(userInfo['auth']))
			id_organizace = int(userInfo['organizace'])
			organizace = get_object_or_404(Organizace, id=id_organizace)
			email = userInfo['email']
			userDetail = {
				'fullName': fullName,
				'organization': organizace.nazev_zkraceny,
				'role_opravneni': role_opravneni,
				'id': user_id,
				'email': email
			}
		else:
			userDetail = {
				'fullName': 'user not logged in',
				'organization': 'user not logged in',
				'role_opravneni': 'user not logged in',
				'id': 'user not logged in',
				'email': 'user not logged in'
			}

	#print(json.dumps(userDetail, indent=1))

	return {'userDetail': userDetail}
