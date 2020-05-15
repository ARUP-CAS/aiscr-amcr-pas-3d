from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps
from . import helper
from . import xmlrpc

import logging

logger = logging.getLogger(__name__)


# Decorator that checks if there is a session ID in the cookie and if not redirects to login
def login_required(func):

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        is_logged_in, user_dict = helper.is_user_logged_in(request)

        if (not is_logged_in):
            return redirect('login')

        # Injecting user to the view functions using the decorator through kwargs
        kwargs['user'] = user_dict

        return func(request, *args, **kwargs)
    return wrapper


def min_user_group(min_group):

    @wraps(min_group)
    def _method_wrapper(func):

        @wraps(func)
        def _arguments_wrapper(request, *args, **kwargs):
            """
            Wrapper with arguments to invoke the method
            """
            sid = request.COOKIES.get('sessionId')

            # Check sid
            if(sid is None):
                # If there is no sid you are not in the group
                logger.debug("sid not found, retrieving new one from the php server")
                return redirect('login')
            else:
                # Otherwise check that you are logged in
                try:
                    user = xmlrpc.get_current_user(sid)
                    if(len(user) == 0):
                        print("Sid " + str(sid) + " no longer valid on the php server.")
                        return redirect('login')
                    else:
                        # Checks that user is in the user group set that is required
                        inMinGroup = helper.min_user_group(user, min_group)
                        # If its not, throw 403
                        if not inMinGroup:
                            raise PermissionDenied("Not sufficient user group privileges.")

                        kwargs['user'] = user

                except Exception as ex:
                    logger.warning("Could not verify current user (php session expired?). Redirecting to login.")
                    logger.error(str(ex))
                    return redirect('login')

                return func(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper
