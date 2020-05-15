from django import forms
from documents.constants import AmcrConstants as c
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from webamcr import helper_general as h


class UserForm(forms.Form):
    ident_cely = forms.CharField(label=_('Identifikátor'), required=False)
    jmeno = forms.CharField(label=_('Jméno'), max_length=100, required=False)
    prijmeni = forms.CharField(label=_('Příjmení'), max_length=100, required=False)
    email = forms.EmailField(label=_('Email'), required=False)
    telefon = forms.CharField(label=_('Telefon'), max_length=15, required=False, validators=[h.validate_phone_number])
    organizace = forms.ChoiceField(label=_('Organizace'), choices=c.ORGANIZATIONS_CACHE, required=False)
    heslo = forms.CharField(label=_('Heslo'), widget=forms.PasswordInput(), required=False)
    heslo_kontrola = forms.CharField(label=_('Heslo pro kontrolu'), widget=forms.PasswordInput(), required=False)
    jazyk = forms.ChoiceField(label=_('Jazyk'), choices=settings.LANGUAGES, required=False)


class CreateUserForm(forms.Form):
    manage_username = forms.CharField(label=_('Jméno'))
    manage_surname = forms.CharField(label=_('Příjmení'))
    manage_email = forms.EmailField(label=_('Email'))
    manage_phone_number = forms.CharField(label=_('Telefon'), max_length=15,
                                          required=False, validators=[h.validate_phone_number])
    manage_organization = forms.ChoiceField(label=_('Organizace'), choices=c.ORGANIZATIONS_CACHE)
    manage_password = forms.CharField(label=_('Heslo'), widget=forms.PasswordInput())
    manage_password_control = forms.CharField(label=_('Heslo pro kontrolu'), widget=forms.PasswordInput())
    manage_role = forms.ChoiceField(label=_('Role'), choices=c.USER_ROLES)
    manage_permissions = forms.MultipleChoiceField(label=_('Oprávnění'), required=False, choices=c.USER_PERMISSIONS)


class EditUserForm(CreateUserForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manage_password'].required = False
        self.fields['manage_password_control'].required = False
        self.fields['manage_phone_number'].required = False
        self.fields['manage_email'].widget.attrs['readonly'] = True
