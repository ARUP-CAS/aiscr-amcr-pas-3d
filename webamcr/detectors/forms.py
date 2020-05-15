from django import forms
from django.utils.translation import gettext_lazy as _

from detectors import connector
from .constants import DetectorConstants as det_const
from documents import helper as helper_doc
from documents.constants import AmcrConstants as c


def make_CreateDetectorForm(user_id, user_sid, initial={}, editProject=False):
    class CreateDetectorForm(forms.Form):
        LOCAL_USER_CACHE = helper_doc.load_user_cache(user_sid)
        LOCAL_PROJECT_CACHE = helper_doc.load_project_cache(user_sid)
        if editProject:
            LOCAL_PROJECT_CACHE = connector.load_my_projects(str(user_id), LOCAL_PROJECT_CACHE)
        projekt_choices = [(i[0], i[1]) for i in LOCAL_PROJECT_CACHE]

        detector_project = forms.ChoiceField(label=_('Projekt'), choices=[('', '')] + projekt_choices, required=True)
        detector_cadastry = forms.CharField(label=_('Katastrální území'),  widget=forms.TextInput(
        attrs={'placeholder': _('Vyplněno automaticky')}), required=False)
        detector_localization = forms.CharField(label=_('Lokalizace'))
        detector_system_coordinates = forms.ChoiceField(
            label=_('Souř. systém'), choices=c.COORDINATE_SYSTEM_CACHE, required=False)
        detector_coordinates_x = forms.CharField(label=_('Šířka (N / Y)'), required=False)
        detector_coordinates_y = forms.CharField(label=_('Délka (E / X)'), required=False)
        #detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=LOCAL_USER_CACHE, required=True)
        LOCAL_NAME_CACHE = helper_doc.load_name_cache(user_sid)
        detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=LOCAL_NAME_CACHE, required=True)
        detector_find_date = forms.CharField(label=_('Datum nálezu'))
        detector_circumstances = forms.ChoiceField(label=_('Nálezové okolnosti'), choices=[
                                                   ('', '')] + c.CIRCUMSTANCE_CACHE, required=True)
        detector_depth = forms.IntegerField(min_value=0, max_value=2147483647, label=_('Hloubka (cm)'), required=False)
        detector_dating = forms.CharField(label=_('Období'), widget=forms.Select(
            choices=[('', '')] + c.PERIOD_12_CACHE), required=True)
        detector_exact_dating = forms.CharField(label=_('Přesná datace'), required=False)
        detector_kind = forms.CharField(label=_('Nález'), widget=forms.Select(
            choices=[('', '')] + c.PREDMET_KIND_CACHE), required=True)
        detector_material = forms.ChoiceField(
            label=_('Materiál'), choices=[('', '')] + c.OBJECT_SPECIFICATION_CACHE, required=True)
        detector_quantity = forms.CharField(label=_('Počet'), required=False)
        detector_note = forms.CharField(label=_('Poznámka / bližší popis'), required=False)
        detector_photo = forms.ImageField(required=False)
        detector_organisation_passed = forms.ChoiceField(
            label=_('Předáno organizaci'), choices=c.ORGANIZATIONS_CACHE, required=False,)
        detector_evidence_number = forms.CharField(label=_('Evidenční číslo'), required=False)
        detector_find_passed = forms.ChoiceField(label=_('Nález předán'), choices=c.BOOL_CHOICES, required=False)
        detector_accessibility = forms.ChoiceField(label=_('Přístupnost'), choices=c.ACCESSIBILITY_CACHE, required=False)
        detector_type = forms.ChoiceField(label=_('Typ nálezu'), choices=c.OBJECT_TYPE_CACHE, required=False)

    return CreateDetectorForm(initial)


def make_ChooseDetectorForm(user_id, user_sid, initial={}):
    class ChooseDetectorForm(forms.Form):
        LOCAL_PROJECT_CACHE = helper_doc.load_project_cache(user_sid)
        LOCAL_PROJECT_CACHE = connector.load_my_projects(str(user_id), LOCAL_PROJECT_CACHE)
        LOCAL_PROJECT_CACHE = [(-1, '')] + LOCAL_PROJECT_CACHE
        PERIOD_012_CACHE = [('', ((-1, ''),))] + c.PERIOD_12_CACHE
        OBJEKT_KIND0_CACHE = [('', ((-1, ''),))] + c.PREDMET_KIND_CACHE
        LOCAL_USER_CACHE = [(-1, '')] + helper_doc.load_user_cache()
        detector_project_id = forms.CharField(label=_('Projekt'), required=False)
        detector_finding_id = forms.CharField(label=_('ID nálezu'), required=False)
        detector_process_state = forms.ChoiceField(label=_('Procesní stavy'), choices=[
                                                   ('', '')] + det_const.DETECTOR_STATE_CACHE, required=False)
        detector_cadastry = forms.ChoiceField(label=_('Katastrální území'), choices=[
                                              ('', '')] + c.CADASTRE_1_CACHE, required=False)
        detector_region = forms.ChoiceField(label=_('Kraj'), choices=[(-1, '')] + c.REGIONS_CACHE, required=False)
        detector_district = forms.ChoiceField(label=_('Okres'), choices=[(-1, '')] + c.DISTRICTS_CACHE, required=False)
        detector_watch_changes = forms.CharField(label=_('Sledovat změny'), required=False)
        detector_cadastre = forms.ChoiceField(label=_('Katastr'), choices=c.CADASTRE_1_CACHE, required=False)
        LOCAL_NAME_CACHE = helper_doc.load_name_cache(user_sid)
        LOCAL_NAME_CACHE = [(-1, '')] + LOCAL_NAME_CACHE
        detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=LOCAL_NAME_CACHE, required=True)
        #detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=LOCAL_USER_CACHE, required=False)
        detector_date_of_change_from = forms.CharField(label=_('Datum změny od'), required=False)
        detector_date_of_change_to = forms.CharField(label=_('Datum změny do'), required=False)
        detector_find_date_from = forms.CharField(label=_('Nalezeno od'), required=False)
        detector_find_date_to = forms.CharField(label=_('Nalezeno do'), required=False)
        detector_user = forms.ChoiceField(label=_('Uživatel'), choices=LOCAL_USER_CACHE, required=False)
        detector_description_details = forms.CharField(label=_('Popisné údaje'), required=False)
        detector_dating = forms.CharField(label=_('Období'), widget=forms.Select(choices=PERIOD_012_CACHE), required=False)
        detector_kind = forms.ChoiceField(label=_('Nález'), choices=OBJEKT_KIND0_CACHE, required=False)
        detector_material = forms.ChoiceField(
            label=_('Materiál'), choices=[('', '')] + c.OBJECT_SPECIFICATION_CACHE, required=False)
        detector_organisation = forms.ChoiceField(
            label=_('Organizace'), choices=[('', '')] + c.ORGANIZATIONS_CACHE, required=False)
        #detector_project_leader = forms.ChoiceField(label=_('Vedoucí projektu'), choices=LOCAL_USER_CACHE, required=False)
        detector_project_leader = forms.ChoiceField(label=_('Vedoucí projektu'), choices=LOCAL_NAME_CACHE, required=False)
        detector_evidence_number = forms.CharField(label=_('Evidenční číslo'), required=False)
        detector_find_passed = forms.ChoiceField(label=_('Předáno'), choices=c.BOOL_WITH_BOTH_CHOICES, required=False)
        detector_accessibility = forms.ChoiceField(label=_('Přístupnost'), choices=[
                                                   ('', '')] + c.ACCESSIBILITY_CACHE, required=False)
    return ChooseDetectorForm(initial)


class CreateCooperateForm(forms.Form):

    archeolog = forms.EmailField(label=_("Archeolog"), required=True)


class UpdateCooperateForm(forms.Form):

    aktivni = forms.BooleanField(label=_('Aktivní'), required=False)
    potvrzeno = forms.BooleanField(label=_('Potvrzeno'), required=False)


class ReturnFindingForm(forms.Form):

    reason = forms.CharField(label=_("Důvod vrácení"), required=True)
