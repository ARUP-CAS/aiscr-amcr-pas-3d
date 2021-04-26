from django import forms
from django.utils.translation import gettext_lazy as _

from detectors import connector
from .constants import DetectorConstants as det_const
from documents.constants import AmcrConstants as c
from webamcr.views import (heslar_pristupnost, heslar_organizace, heslar_spz_storage,
    heslar_specifikace_predmetu, heslar_typ_nalezu, heslar_predmet_12, heslar_obdobi_12,
    heslar_nalezove_okolnosti)


def make_CreateDetectorForm(user_id, user_sid, initial={}, editProject=False):
    class CreateDetectorForm(forms.Form):
        projekty = connector.projekty_vyzkumne()
        if editProject: # zapisuju novy nalez
            projekty = connector.projekty_zahajene_ukoncene_v_terenu(projekty)
            projekty = connector.load_my_projects(str(user_id), projekty)
        projekt_choices = [(i['id'], i['ident_cely'] + ' (' + connector.get_vypis_cely_by_id_name(i['vedouci_projektu']) + ')') for i in projekty]
        detector_project = forms.ChoiceField(
            label=_('Projekt'), 
            choices=[('', '')] + projekt_choices, 
            required=True,
            )
        detector_cadastry = forms.CharField(label=_('Katastrální území'),  widget=forms.TextInput(
            attrs={'placeholder': _('Vyplněno automaticky')}), required=False)
        detector_localization = forms.CharField(
            label=_('Lokalizace'), 
            required=False,
            widget=forms.TextInput(attrs={'title':_("Slovní popis lokalizace formou parcelního čísla a/nebo pomístního jména (jména ulic, tratí, poloh).")}),
            )
        detector_system_coordinates = forms.ChoiceField(
            label=_('Souř. systém'), choices=c.COORDINATE_SYSTEM_CACHE, required=False)
        detector_coordinates_x = forms.CharField(label=_('Šířka (N / Y)'), required=False)
        detector_coordinates_y = forms.CharField(label=_('Délka (E / X)'), required=False)
        detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=connector.prijmeni_jmeno(), required=False)
        detector_find_date = forms.CharField(label=_('Datum nálezu'), required=False)
        detector_circumstances = forms.ChoiceField(label=_('Nálezové okolnosti'), choices=heslar_nalezove_okolnosti(), required=False)
        detector_depth = forms.IntegerField(
            min_value=0, 
            max_value=2147483647, 
            label=_('Hloubka (cm)'), 
            required=False,
            widget=forms.TextInput(attrs={'title':_("Přibližná hloubka, ze které byl nález získán. Povrchové nálezy označte hloubkou 0.")}),
            )
        detector_dating = forms.CharField(label=_('Období'), widget=forms.Select(choices=heslar_obdobi_12()), required=False)
        detector_exact_dating = forms.CharField(
            label=_('Přesná datace'), 
            required=False,
            widget=forms.TextInput(attrs={'title':_("Upřesněná datace, např. pomocí roku (pro mince) nebo stupňů (Lt B2/C1; nikoli však pouze B2/C1).")}),
            )
        detector_kind = forms.CharField(label=_('Nález'), widget=forms.Select(
            choices=heslar_predmet_12()), required=False)
        detector_material = forms.ChoiceField(
            label=_('Materiál'), choices=heslar_specifikace_predmetu(), required=False)
        detector_quantity = forms.CharField(label=_('Počet'), required=False)
        detector_note = forms.CharField(
            label=_('Poznámka / bližší popis'), 
            required=False,
            widget=forms.TextInput(attrs={'title':_("Interpretace či bližší popis nálezu a jeho okolností.")}),
            )
        detector_photo = forms.ImageField(required=False)
        detector_organisation_passed = forms.ChoiceField(
            label=_('Předáno organizaci'), choices=heslar_organizace(), required=False,)
        detector_evidence_number = forms.CharField(
            label=_('Evidenční číslo'), 
            required=False,
            widget=forms.TextInput(attrs={'title':_("Označení nálezu v organizaci, které byl předán. V případě využití čísla podle AMČR-PAS doplňte pouze \"PAS\".")}),
            )
        detector_find_passed = forms.ChoiceField(label=_('Nález předán'), choices=c.BOOL_CHOICES, required=False)
        detector_accessibility = forms.ChoiceField(label=_('Přístupnost'), choices=heslar_pristupnost(), required=False)
        detector_type = forms.ChoiceField(label=_('Typ nálezu'), choices=heslar_typ_nalezu(), required=False)

    return CreateDetectorForm(initial)


def make_ChooseDetectorForm(user_id, user_sid, initial={}):
    class ChooseDetectorForm(forms.Form):
        detector_project_id = forms.CharField(label=_('Projekt'), required=False)
        detector_finding_id = forms.CharField(label=_('ID nálezu'), required=False)
        detector_process_state = forms.ChoiceField(label=_('Procesní stavy'), choices=[
                                                   ('', '')] + det_const.DETECTOR_STATE_CACHE, required=False)
        #detector_cadastry = forms.ChoiceField(label=_('Katastrální území'), choices=[
        #                                      ('', '')] + c.CADASTRE_12_CACHE, required=False)
        detector_district = forms.ChoiceField(label=_('Okres'), choices=heslar_spz_storage(), required=False)
        detector_watch_changes = forms.CharField(label=_('Sledovat změny'), required=False)
        detector_finder = forms.ChoiceField(label=_('Nálezce'), choices=[(-1, '')] + list(connector.prijmeni_jmeno()), required=True)
        detector_date_of_change_from = forms.CharField(label=_('Datum změny od'), required=False)
        detector_date_of_change_to = forms.CharField(label=_('Datum změny do'), required=False)
        detector_find_date_from = forms.CharField(label=_('Nalezeno od'), required=False)
        detector_find_date_to = forms.CharField(label=_('Nalezeno do'), required=False)
        detector_description_details = forms.CharField(label=_('Popisné údaje'), required=False)
        detector_dating = forms.CharField(label=_('Období'), widget=forms.Select(choices=heslar_obdobi_12()), required=False)
        detector_kind = forms.ChoiceField(label=_('Nález'), choices=heslar_predmet_12(), required=False)
        detector_material = forms.ChoiceField(
            label=_('Materiál'), choices=heslar_specifikace_predmetu(), required=False)
        detector_organisation = forms.ChoiceField(
            label=_('Organizace'), choices=heslar_organizace(), required=False)
        detector_project_leader = forms.ChoiceField(label=_('Vedoucí projektu'), choices=[(-1, '')] + list(connector.prijmeni_jmeno()), required=False)
        detector_evidence_number = forms.CharField(label=_('Evidenční číslo'), required=False)
        detector_find_passed = forms.ChoiceField(label=_('Předáno'), choices=c.BOOL_WITH_BOTH_CHOICES, required=False)
        detector_accessibility = forms.ChoiceField(label=_('Přístupnost'), choices=heslar_pristupnost(), required=False)
    return ChooseDetectorForm(initial)


class CreateCooperateForm(forms.Form):

    archeolog = forms.EmailField(label=_("Archeolog"),widget=forms.TextInput(attrs={'placeholder': _('Zadejte email archeologa pro spolupráci')}), required=True)


class UpdateCooperateForm(forms.Form):

    aktivni = forms.BooleanField(label=_('Aktivní'), required=False)
    potvrzeno = forms.BooleanField(label=_('Potvrzeno'), required=False)


class ReturnFindingForm(forms.Form):

    reason = forms.CharField(label=_("Důvod vrácení"), required=True)
