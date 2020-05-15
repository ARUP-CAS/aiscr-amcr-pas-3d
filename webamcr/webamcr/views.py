from django.shortcuts import render, redirect
from django.contrib import messages

from documents.constants import AmcrConstants as c
from documents import helper, xmlrpc
from documents.decorators import login_required

import logging

logger = logging.getLogger(__name__)


@login_required
def home(request, **kwargs):

	isLogged, userDict = helper.is_user_logged_in(request)
	if(not isLogged):
		return redirect('login')

	return render(request, 'home.html')


def err_sid(request, *args, **argv):
	response = render(request, '403.html')
	response.status_code = 403
	return response


@login_required
def delete(request, fileId, **kwargs):

	sid = request.COOKIES.get('sessionId')

	resp = xmlrpc.delete_file(sid, fileId)

	if not resp[0]:
		# Not sure if 404 is the only correct option
		messages.add_message(request, messages.SUCCESS, c.OBEJCT_COULD_NOT_BE_DELETED)
		return render(request, 'error_404.html')
	else:
		logger.debug("Byl smazán soubor s id: " + str(fileId))
		messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)

	return redirect(request.META['HTTP_REFERER'])
