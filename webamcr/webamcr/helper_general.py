import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from detectors.models import UserStorage
from documents.constants import AmcrConstants as c


def get_user_name_from_id(userId):
	user = get_object_or_404(UserStorage , pk = userId)
	return user.jmeno + ' ' + user.prijmeni


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
def build_auth_level(role_id, permissions=[]):

	authLevel = 0
	# Check if the role is Badatel
	role_id_int = int(role_id)
	roles = dict(c.USER_ROLES)

	# Map roles to int value
	if roles[role_id_int] == c.BADATEL:
		authLevel += 1
	elif roles[role_id_int] == c.ARCHEOLOG:
		authLevel += 2
	elif roles[role_id_int] == c.ARCHIVAR:
		authLevel += 16
	elif roles[role_id_int] == c.ADMIN:
		authLevel += 4
		# # TODO finish this method user admin???

	# Map permissions to int value
	for permission in permissions:
		if int(permission) == c.ADMIN3D_ID:
			authLevel += 128
		if int(permission) == c.ACCOUNTS_ADMIN_ID:
			authLevel += 64
		#if int(permission) == c.ARCHIVAR_DETECTORS_ID:
		#	authLevel += 32
		if int(permission) == c.USERS_ADMIN_ID:
			authLevel += 8

	return authLevel


def validate_phone_number(number):
	number = number.replace(" ","")
	SVK = '+421'
	CZE = '+420'
	isValid = False
	r = re.compile('[0-9]+')
	# With country code
	if number.startswith(SVK) or number.startswith(CZE) :
		rest = number[4:] # Without the country code
		if(len(rest) == 9 and r.match(rest)):
			#+421 907 452 325 or +420 722 803 058
			isValid = True
			#0907 452 325 or 722 803 058
	# Without country code
	elif (len(number) == 10 or len(number) == 9 and r.match(number)):
		isValid = True

	if(not isValid):
		raise ValidationError(
			_('%(value)s nesprávný formát čísla. Musí být: +420xxxxxxxxx'),
			params={'value': number},
		)


