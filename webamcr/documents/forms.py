from django import forms
from django.utils.translation import gettext_lazy as _
from .constants import AmcrConstants as c
from webamcr.views import (heslar_zeme, heslar_organizace, heslar_specifikace_predmetu,
    heslar_typ_nalezu, heslar_format_dokumentu, heslar_typ_dokumentu, heslar_objekt_12,
    heslar_predmet_12, heslar_obdobi_12, heslar_areal_12, heslar_specifikace_objektu_12)


class ChooseForm(forms.Form):

    ident_cely = forms.CharField(label=_('ID obsahuje'), widget=forms.TextInput(
        attrs={'placeholder': _('Všechna ID')}), required=False)
    rok_vzniku = forms.CharField(label=_('Rok vzniku'), required=False)
    popis = forms.CharField(label=_('Popisné údaje obsahují'), required=False)
    duveryhodnost = forms.CharField(label=_('Minimální důvěryhodnost'), required=False)
    procesni_stavy = forms.MultipleChoiceField(
        label=_('Procesní stavy'), choices=c.DOCUMENT_STATE_CACHE, required=False)
    aktivity = forms.MultipleChoiceField(label=_('Aktivity'), required=False, choices=c.COMPONENT_ACTIVITIES)

    zmeny = forms.MultipleChoiceField(label=_('Sledovat změny'), choices=[('', '')] + c.TYPY_ZMENY_MODELU, required=False)
    zmena_od = forms.CharField(label=_('Změna od'), required=False)
    zmena_do = forms.CharField(label=_('Změna do'), required=False)

    def __init__(self, *args, names, users, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['autori'] = forms.MultipleChoiceField(
            label=_("Autoři"),
            required=False,
            choices=names
        )
        self.fields['zmena_uzivatel'] = forms.ChoiceField(
            label=_("Uživatel"),
            required=False,
            choices=[('', '')] + users
        )
        self.fields['organizace'] = forms.ChoiceField(
            label=_('Organizace'), choices=heslar_organizace(), required=False)
        self.fields['specifikace_predmetu'] = forms.MultipleChoiceField(
            label=_('Specifikace předmětu'), choices=heslar_specifikace_predmetu(), required=False)
        self.fields['typ_dokumentu'] = forms.ChoiceField(
            label=_('Typ dokumentu'), choices=heslar_typ_dokumentu(), required=False)
        self.fields['druh_objektu'] = forms.CharField(
            label=_('Druh objektu'), widget=forms.Select(choices=heslar_objekt_12()), required=False)
        self.fields['druh_predmetu'] = forms.CharField(
            label=_('Druh předmětu'), widget=forms.Select(choices=heslar_predmet_12()), required=False)
        self.fields['obdobi'] = forms.MultipleChoiceField(label=_('Období'), choices=heslar_obdobi_12(), required=False)
        self.fields['areal'] = forms.CharField(label=_('Areál'), widget=forms.Select(choices=heslar_areal_12()), required=False)
        self.fields['specifikace_objektu'] = forms.CharField(
            label=_('Specifikace objektu'), widget=forms.Select(choices=heslar_specifikace_objektu_12()), required=False)

    def getClenedData(self):

        print("Getting data from the form...")
        for field_data in self.cleaned_data:
            if field_data:
                print(field_data)
            else:
                print(str(field_data) + 'is empty')


class CreateForm(forms.Form):
    rok_vzniku = forms.CharField(label=_('Rok vzniku'), required=True)
    oznaceni_originalu = forms.CharField(label=_('Označení originálu'), required=False)
    popis = forms.CharField(label=_('Popis'), widget=forms.Textarea(), required=True)
    poznamka = forms.CharField(label=_('Poznámka'), widget=forms.Textarea(), required=False)
    duveryhodnost = forms.CharField(label=_('Důvěryhodnost'), required=True)
    region = forms.CharField(label=_('Region'), required=False)
    sirka = forms.CharField(label=_('Šířka (N / Y)'), required=False)
    delka = forms.CharField(label=_('Délka (E / X)'), required=False)

    presna_datace = forms.CharField(label=_('Přesná datace'), required=False)
    aktivity = forms.MultipleChoiceField(label=_('Aktivity'), required=False, choices=c.COMPONENT_ACTIVITIES)
    # Extra data
    odkaz = forms.CharField(label=_('Odkaz'), required=False)

    def __init__(self, *args, readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizace_autora'] = forms.ChoiceField(
            label=_('Organizace'), choices=heslar_organizace(), required=True)
        self.fields['zeme'] = forms.ChoiceField(label=_('Země'), choices=heslar_zeme(), required=False)
        self.fields['format'] = forms.ChoiceField(label=_('Formát'), choices=heslar_format_dokumentu(), required=True)
        self.fields['typ_dokumentu'] = forms.ChoiceField(
            label=_('Typ dokumentu'), choices=heslar_typ_dokumentu(), required=True)
        self.fields['obdobi'] = forms.CharField(label=_('Období'), widget=forms.Select(
            choices=heslar_obdobi_12()), required=False)
        self.fields['areal'] = forms.CharField(label=_('Areál'), widget=forms.Select(
            choices=heslar_areal_12()), required=False)
        for key in self.fields.keys():
            self.fields[key].disabled = readonly


class FindingDocumentForm(forms.Form):
    poznamka = forms.CharField(label=_('Poznámka'), widget=forms.Textarea(), required=False)
    pocet = forms.CharField(label=_('Počet'), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['typ_nalezu'] = forms.ChoiceField(label=_('Typ nálezu'), choices=heslar_typ_nalezu(), required=True)
        self.fields['specifikace_predmetu'] = forms.ChoiceField(
            label=_('Specifikace předmětu'), choices=heslar_specifikace_predmetu(), required=False)
        self.fields['druh_objektu'] = forms.CharField(
            label=_('Druh objektu'), widget=forms.Select(choices=heslar_objekt_12()), required=False)
        self.fields['druh_predmetu'] = forms.CharField(
            label=_('Druh předmětu'), widget=forms.Select(choices=heslar_predmet_12()), required=False)
        self.fields['specifikace_objektu'] = forms.CharField(
            label=_('Specifikace objektu'), widget=forms.Select(choices=heslar_specifikace_objektu_12()), required=False)


class LoginForm(forms.Form):
    login_username = forms.CharField(label=_('Uživatelské jméno (email)'), max_length=100)
    login_password = forms.CharField(label=_('Heslo'), widget=forms.PasswordInput())


class AddNameForm(forms.Form):
    jmeno = forms.CharField(label=_('Jméno'), max_length=100)
    prijmeni = forms.CharField(label=_('Příjmení'), max_length=100)


class EditAuthorForm(forms.Form):

    def __init__(self, *args, names, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author1'] = forms.ChoiceField(
            label=_("První autor"),
            required=False,
            choices=names)
        self.fields['author2'] = forms.ChoiceField(
            label=_("Druhý autor"),
            required=False,
            choices=names)
        self.fields['author3'] = forms.ChoiceField(
            label=_("Třetí autor"),
            required=False,
            choices=names)
        self.fields['author4'] = forms.ChoiceField(
            label=_("Čtvrtý autor"),
            required=False,
            choices=names)
        self.fields['author5'] = forms.ChoiceField(
            label=_("Pátý autor"),
            required=False,
            choices=names)
        self.fields['author6'] = forms.ChoiceField(
            label=_("Šestý autor"),
            required=False,
            choices=names)
        self.fields['author7'] = forms.ChoiceField(
            label=_("Sedmý autor"),
            required=False,
            choices=names)
        self.fields['author8'] = forms.ChoiceField(
            label=_("Osmý autor"),
            required=False,
            choices=names)
        self.fields['author9'] = forms.ChoiceField(
            label=_("Devátý autor"),
            required=False,
            choices=names)
        self.fields['author10'] = forms.ChoiceField(
            label=_("Desátý autor"),
            required=False,
            choices=names)
