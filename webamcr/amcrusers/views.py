import hashlib

from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.views.generic.list import ListView
from django.contrib import messages

from .forms import UserForm, CreateUserForm, EditUserForm
from documents import xmlrpc
from documents.decorators import login_required, min_user_group
from django.forms.models import model_to_dict
from detectors.models import UserStorage
from webamcr import helper_general as helper
from detectors import models as m
from documents import helper as doc_helper
from documents.constants import AmcrConstants as c
from . import user_helper

import logging

logger = logging.getLogger(__name__)


@min_user_group(c.ADMIN)
def users_list(request, **kwargs):

    #start = time.time()

    context = user_helper.get_all_users()
    response = render(request, 'amcrusers/users.html', {'context': context})

    #end = time.time()
    #print(end - start)

    return response


class UsersList(ListView):

    paginate_by = 10
    model = UserStorage
    template_name = "amcrusers/userstorage_list.html"


@min_user_group(c.ADMIN)
def user_create(request, **kwargs):

    sid = request.COOKIES.get('sessionId')
    message = {}

    if(request.method == 'POST'):
        form = CreateUserForm(request.POST)
        if form.is_valid():

            manage_username = form.cleaned_data['manage_username']
            manage_surname = form.cleaned_data['manage_surname']
            manage_phone_number = form.cleaned_data['manage_phone_number']
            manage_password = form.cleaned_data['manage_password']
            manage_password_control = form.cleaned_data['manage_password_control']
            manage_organization = form.cleaned_data['manage_organization']
            manage_email = form.cleaned_data['manage_email']
            manage_role_id = form.cleaned_data['manage_role']
            manage_permissions = form.cleaned_data['manage_permissions']

            # Check that the passwords are the same
            if manage_password != manage_password_control:
                logger.debug("Hesla se neshodují")
                form.add_error('manage_password_control', 'Hesla se neshodují')
            else:
                # md5 of the pass and check that it is the same
                passHash = hashlib.sha1(manage_password.encode('utf8')).hexdigest()

                # Getting auth level based on roles and permissions
                authLevel = helper.build_auth_level(manage_role_id, manage_permissions)

                # Creratin the user using xmlrpc request
                resp = xmlrpc.zmena(sid, 'uzivatel', 'create',
                                    {
                                        'news': False,
                                        'vypis': manage_surname + ', ' + manage_username.upper()[0] + '.',
                                        'pasw': passHash,
                                        'auth': authLevel,
                                        'telefon': manage_phone_number,
                                        'prijmeni': manage_surname,
                                        'jmeno': manage_username,
                                        'organizace': manage_organization,
                                        'email': manage_email
                                    }
                                    )

                if resp[0]:
                    logger.debug("User with id created: " + str(resp[1]))
                    message['type'] = c.SUCCESS
                    message['text'] = c.OBJECT_CREATED_SUCCESSFULLY
                    return redirect('amcrusers:users_list')
                else:
                    logger.debug("Could not create user: " + str(resp[1]))
                    message['type'] = c.ERROR
                    message['text'] = resp[1]

                # newUser = UserStorage(
                #   jmeno=manage_username,
                #   email=manage_email,
                #   pasw =passHash,
                #   auth_level=0, # auth level is actually stored into anotherTable: user_group_auth_storage,
                #   telefon=manage_phone_number,
                #   organizace=manage_organization, # also stored in atree table
                #   news='',
                #   prijmeni=manage_surname,
                #   confirmation=False
                #   )

        else:
            logger.debug("Form is not valid: " + str(form.errors))

        print(form.errors)

    else:
        form = CreateUserForm()

    return render(request, 'amcrusers/user_create.html', {
        'form': form,
        'context': {
            'title': 'Nový uživatel',
            'message': message
        }
    })


@min_user_group(c.ADMIN)
def user_edit(request, pk, **kwargs):

    message = {}
    sid = request.COOKIES.get('sessionId')
    user = get_object_or_404(UserStorage, pk=pk)
    auth_records = dict(m.UserGroupAuthStorage.objects.filter(
        id__item_type=-10).values_list('user_group', 'auth_level'))

    # What is auth_level of the user
    auth_level = user_helper.get_auth_level(user, auth_records)

    rolesAndPerm = doc_helper.get_roles_and_permissions(auth_level)
    permissions = []
    for perm in rolesAndPerm['opravneni']:
        permissions.append(str(c.USER_PERMISSIONS_DICT[perm]))

    if(request.method == 'POST'):

        form = EditUserForm(request.POST)

        if form.is_valid():

            params = {'id': user.id.id}

            manage_username = form.cleaned_data['manage_username']
            manage_surname = form.cleaned_data['manage_surname']
            manage_phone_number = form.cleaned_data['manage_phone_number']
            manage_password = form.cleaned_data['manage_password']
            manage_password_control = form.cleaned_data['manage_password_control']
            manage_organization = form.cleaned_data['manage_organization']
            manage_email = form.cleaned_data['manage_email']
            manage_role_id = form.cleaned_data['manage_role']
            manage_permissions = form.cleaned_data['manage_permissions']

            # Check that the passwords are the same
            if manage_password != manage_password_control:
                logger.debug("Hesla se neshodují")
                form.add_error('manage_password_control', 'Hesla se neshodují')
            else:

                # Getting auth level based on roles and permissions
                authLevel = helper.build_auth_level(manage_role_id, manage_permissions)

                # Check what has been changed
                if manage_username != user.jmeno:
                    params['jmeno'] = manage_username
                if manage_surname != user.prijmeni:
                    params['prijmeni'] = manage_surname
                if manage_phone_number != user.telefon:
                    params['telefon'] = manage_phone_number
                if int(manage_organization) != user.organizace.id:
                    params['organizace'] = manage_organization
                if manage_email != user.email:
                    params['email'] = manage_email
                if (int(manage_role_id) != c.USER_ROLES_DICT[rolesAndPerm['role']]) or (manage_permissions != permissions):
                    params['auth'] = authLevel
                if (len(manage_password) > 0) and (manage_password != user.pasw):
                    params['pasw'] = hashlib.sha1(manage_password.encode('utf8')).hexdigest()

                # Update the user using xmlrpc request
                resp = xmlrpc.zmena(sid, 'uzivatel', 'update', params)

                if resp[0]:
                    logger.debug("User with id updated: " + str(resp[1]))
                    message['type'] = c.SUCCESS
                    message['text'] = c.OBJECT_UPDATED_SUCCESSFULLY
                else:
                    logger.debug("Could not update user: " + str(resp[1]))
                    message['type'] = c.ERROR
                    message['text'] = resp[1]

                context = user_helper.get_all_users()
                context['message'] = message
                return render(request, 'amcrusers/users.html', {'context': context})

        else:
            print("Form is not valid")
    else:

        # Create form
        form = EditUserForm(
            {
                'manage_username': user.jmeno,
                'manage_surname': user.prijmeni,
                'manage_organization': user.organizace.id,
                'manage_email': user.email,
                'manage_permissions': permissions,
                'manage_role': c.USER_ROLES_DICT[rolesAndPerm['role']],
                'manage_phone_number': user.telefon
            })

        print(form.errors)

    return render(request, 'amcrusers/user_create.html', {
        'form': form,
        'context': {
            'title': 'Editace uživatele',
        }
    })


@login_required
def userDetail(request, **kwargs):

    curr_user = kwargs['user']  # xmlrpc.get_current_user(sid)
    message = {}
    context = {}
    user = get_object_or_404(UserStorage, pk=curr_user.get('id'))

    if(request.method == 'POST'):
        formUser = UserForm(request.POST)
        if formUser.is_valid():
            user_number = formUser.cleaned_data['telefon']
            user_notification_set = request.POST.get('notifikace_nalezu')
            user_password = formUser.cleaned_data['heslo']
            user_password_check = formUser.cleaned_data['heslo_kontrola']
            user_language = formUser.cleaned_data['jazyk']

            if user_notification_set == 'ano':
                user.notifikace_nalezu = True
            else:
                user.notifikace_nalezu = False
            user.telefon = user_number
            if user.jazyk != user_language:
                user.jazyk = user_language
                messages.add_message(request, messages.SUCCESS, c.LANGUAGE_CHANGED_MSG)

            if (user_password == user_password_check) and user_password:
                user.pasw = hashlib.sha1(user_password.encode('utf8')).hexdigest()

            user.save()

            logger.debug("User with id updated: " + str(user.id))
            message['type'] = c.SUCCESS
            message['text'] = c.OBJECT_UPDATED_SUCCESSFULLY
        else:
            print("Form is not valid")
            print(formUser.non_field_errors)
            print(formUser.errors)
            render(request, 'amcrusers/user_detail.html', {'formUser': formUser, 'current_user': model_to_dict(user)})

    context['message'] = message
    data = {
        'ident_cely': user.ident_cely,
        'jmeno': user.jmeno,
        'prijmeni': user.prijmeni,
        'email': user.email,
        'telefon': user.telefon,
        'organizace': user.organizace.id,
        'jazyk': user.jazyk
    }
    formUser = UserForm(data)

    response = render(request, 'amcrusers/user_detail.html', {
        'formUser': formUser,
        'current_user': user,
        'notifikace_nalezu': user.notifikace_nalezu,
        'context': context
    })

    doc_helper.set_cookie(response, 'django_language', user.jazyk)
    return response


@min_user_group(c.ADMIN)
def user_delete(request, pk, **kwargs):

    message = {}
    sid = request.COOKIES.get('sessionId')

    resp = xmlrpc.zmena(sid, 'uzivatel', 'delete', {
        'id': str(pk)
    })

    if not resp[0]:
        message['type'] = c.ERROR
        message['text'] = resp[1]
    else:
        message['type'] = c.SUCCESS
        message['text'] = c.OBJECT_DELETED_SUCCESSFULLY

    context = user_helper.get_all_users()
    context['message'] = message

    return render(request, 'amcrusers/users.html', {
        'context': context})
