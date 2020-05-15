from detectors.models import UserStorage, UserGroupAuthStorage
from documents import helper as doc_helper
from documents.constants import AmcrConstants as c

import logging

logger = logging.getLogger(__name__)


def get_all_users():
    context = {}
    users_list = []
    # Show all except system users (SmartGIS users)
    users = UserStorage.objects.select_related('organizace', 'id').all().exclude(organizace=3)
    auth_records = dict(UserGroupAuthStorage.objects.filter(id__item_type=-10).values_list('user_group', 'auth_level'))

    for user in users:
        user.organizace_zkr = c.ORGANIZATIONS_CACHE_DICT[user.organizace.id]
        auth_level = get_auth_level(user, auth_records)
        rolesAndPerm = doc_helper.get_roles_and_permissions(auth_level)
        user_dict = user.__dict__
        user_dict['role'] = rolesAndPerm['role']
        user_dict['opravneni'] = rolesAndPerm['opravneni']
        users_list.append(user_dict)

    context['uzivatele'] = users_list
    return context


def get_auth_level(user, auth_records):

    auth_level = 0

    try:
        auth_level = auth_records[user.id.id]
    except KeyError:
        logger.warning("User group auth storage with type -10 for user : " + str(user.email) + " not presnet!")

    if auth_level is None:
        logger.warning("Auth_level for user : " + str(user.email) + " not set!")
        auth_level = 0

    return auth_level
