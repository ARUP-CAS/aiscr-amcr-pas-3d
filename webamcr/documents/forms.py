from django import forms
from django.utils.translation import gettext_lazy as _
from .constants import AmcrConstants as c


class ChooseForm(forms.Form):

    ident_cely = forms.CharField(label=_('ID obsahuje'), widget=forms.TextInput(
        attrs={'placeholder': _('Všechna ID')}), required=False)
    rok_vzniku = forms.CharField(label=_('Rok vzniku'), required=False)
    organizace = forms.ChoiceField(label=_('Organizace'), choices=[('', '')] + c.ORGANIZATIONS_CACHE, required=False)
    typ_dokumentu = forms.ChoiceField(label=_('Typ dokumentu'), choices=[
                                      ('', '')] + c.DOCUMENT_TYPE_CACHE, required=False)
    popis = forms.CharField(label=_('Popisné údaje obsahují'), required=False)
    duveryhodnost = forms.CharField(label=_('Minimální důvěryhodnost'), required=False)
    procesni_stavy = forms.MultipleChoiceField(
        label=_('Procesní stavy'), choices=c.DOCUMENT_STATE_CACHE, required=False)

    obdobi = forms.MultipleChoiceField(label=_('Období'), choices=[('', '')] + c.PERIOD_12_CACHE, required=False)
    areal = forms.CharField(label=_('Areál'), widget=forms.Select(
        choices=[('', '')] + c.AREAL_12_CACHE), required=False)
    aktivity = forms.MultipleChoiceField(label=_('Aktivity'), required=False, choices=c.COMPONENT_ACTIVITIES)

    druh_objektu = forms.CharField(
        label=_('Druh objektu'), widget=forms.Select(choices=[('', '')] + c.OBJEKT_KIND_12_CACHE), required=False)
    druh_predmetu = forms.CharField(
        label=_('Druh předmětu'), widget=forms.Select(choices=[('', '')] + c.PREDMET_KIND_CACHE), required=False)
    specifikace_objektu = forms.CharField(
        label=_('Specifikace objektu'), widget=forms.Select(choices=[('', '')] + c.SPECIFICATION_12_CACHE), required=False)
    specifikace_predmetu = forms.ChoiceField(
        label=_('Specifikace předmětu'), choices=[('', '')] + c.OBJECT_SPECIFICATION_CACHE, required=False)

    zmeny = forms.ChoiceField(label=_('Sledovat změny'), choices=[('', '')] + c.TYPY_ZMENY_MODELU, required=False)
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

    def getClenedData(self):

        print("Getting data from the form...")
        for field_data in self.cleaned_data:
            if field_data:
                print(field_data)
            else:
                print(str(field_data) + 'is empty')


class CreateForm(forms.Form):
    typ_dokumentu = forms.ChoiceField(label=_('Typ dokumentu'), choices=[
                                      ('', '')] + c.DOCUMENT_TYPE_CACHE, required=True)
    organizace_autora = forms.ChoiceField(label=_('Organizace'), choices=[
                                          ('', '')] + c.ORGANIZATIONS_CACHE, required=True)
    rok_vzniku = forms.CharField(label=_('Rok vzniku'), required=True)
    oznaceni_originalu = forms.CharField(label=_('Označení originálu'), required=False)
    popis = forms.CharField(label=_('Popis'), widget=forms.Textarea(), required=True)
    poznamka = forms.CharField(label=_('Poznámka'), widget=forms.Textarea(), required=False)
    duveryhodnost = forms.CharField(label=_('Důvěryhodnost'), required=True)
    zeme = forms.ChoiceField(label=_('Země'),  choices=[('', '')] + c.COUNTRIES_CACHE,required=False)
    region = forms.CharField(label=_('Region'), required=False)
    sirka = forms.CharField(label=_('Šířka (N)'), required=False)
    delka = forms.CharField(label=_('Délka (E)'), required=False)

    # Komponenta
    obdobi = forms.CharField(label=_('Období'), widget=forms.Select(
        choices=[('', '')] + c.PERIOD_12_CACHE), required=False)
    areal = forms.CharField(label=_('Areál'), widget=forms.Select(
        choices=[('', '')] + c.AREAL_12_CACHE), required=False)
    presna_datace = forms.CharField(label=_('Přesná datace'), required=False)
    aktivity = forms.MultipleChoiceField(label=_('Aktivity'), required=False, choices=c.COMPONENT_ACTIVITIES)
    # Extra data
    odkaz = forms.CharField(label=_('Odkaz'), required=False)
    format = forms.ChoiceField(label=_('Formát'), choices=[('', '')] + c.FORMAT_CACHE, required=True)

    def __init__(self, *args, readonly=False, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].disabled = readonly


class FindingDocumentForm(forms.Form):
    typ_nalezu = forms.ChoiceField(label=_('Typ nálezu'), choices=[('', '')] + c.OBJECT_TYPE_CACHE, required=True)
    druh_objektu = forms.CharField(
        label=_('Druh objektu'), widget=forms.Select(choices=[('', '')] + c.OBJEKT_KIND_12_CACHE), required=False)
    druh_predmetu = forms.CharField(
        label=_('Druh předmětu'), widget=forms.Select(choices=[('', '')] + c.PREDMET_KIND_CACHE), required=False)
    specifikace_objektu = forms.CharField(
        label=_('Specifikace objektu'), widget=forms.Select(choices=[('', '')] + c.SPECIFICATION_12_CACHE), required=False)
    specifikace_predmetu = forms.ChoiceField(
        label=_('Specifikace předmětu'), choices=[('', '')] + c.OBJECT_SPECIFICATION_CACHE, required=False)
    poznamka = forms.CharField(label=_('Poznámka'), widget=forms.Textarea(), required=False)
    pocet = forms.CharField(label=_('Počet'), required=False)


class LoginForm(forms.Form):
    login_username = forms.CharField(label=_('Uživatelské jméno'), max_length=100)
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
