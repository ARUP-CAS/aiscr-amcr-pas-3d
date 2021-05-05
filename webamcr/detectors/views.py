import logging
import subprocess

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from detectors import helper as helper_det
from documents.constants import AmcrConstants as c
from documents import helper as helper_doc
from documents import xmlrpc
from documents.forms import AddNameForm
from documents.decorators import login_required, min_user_group
from documents.models import (HeslarPredmetDruh, HeslarObdobiDruha,
    HeslarSpecifikacePredmetu)
from webamcr import helper_general
from webamcr.views import heslar_organizace

from . import connector
from . import amcemails
from django.core.files import File
from .constants import DetectorConstants as det_const
from . import models
from .forms import (CreateCooperateForm, UpdateCooperateForm,
                    make_ChooseDetectorForm, make_CreateDetectorForm, ReturnFindingForm)
from io import BytesIO


logger = logging.getLogger(__name__)


@login_required
def upload(request, projectId, findingIdentCely, **kwargs):

    sid = request.COOKIES.get('sessionId')
    nalez = models.SamostatnyNalez.objects.get(ident_cely=findingIdentCely)

    if request.method == 'POST' and request.FILES['myFile']:
        uploadedFile = request.FILES['myFile']
        originalName = uploadedFile.name

        # Check if the file type is allowed
        logger.debug("File name: " + str(originalName))
        allowed_types = ['.jpg', '.jpeg', '.tiff', '.tif', '.png']
        allowed_type = False
        for i in allowed_types:
            if uploadedFile.name.lower().endswith(i):
                allowed_type = True
                break
        if not allowed_type:
            messages.add_message(request, messages.WARNING, _("Pouze soubory typu jpg, tiff a png je možné nahrávat."))
            return render(request, 'detectors/uploadFile.html', {'findingIdentCely': findingIdentCely})
        # Remove EXIF data using exiftools
        args = ['exiftool', '-All=', '-']
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = p.communicate(input=uploadedFile.read())
        sanitized_image = BytesIO(out)
        f_new = File(sanitized_image)
        f_new.name = originalName

        resp = xmlrpc.uploadProjectFile(sid, projectId, f_new, nalez)
        if resp:
            soubor = models.Soubor.objects.get(pk=resp[0])
            soubor.samostatny_nalez = nalez
            soubor.uzivatelske_oznaceni = originalName
            soubor.projekt = None
            soubor.save()
        else:
            logger.warning('Chyba pri uploadu souboru')

        return redirect('/pas/create/' + findingIdentCely)
    return render(request, 'detectors/uploadFile.html', {'findingIdentCely': findingIdentCely})


@login_required
@csrf_protect
def index(request, **kwargs):
    response = render(request, 'detectors/index.html')
    return response


def logout(request):
    response = redirect('login')
    response.delete_cookie('sessionId')
    response.delete_cookie('lstamp')
    return response


@login_required
def create(request, ident_cely='0', **kwargs):
    projekt_id = []
    user_sid = request.COOKIES.get('sessionId')
    current_user = kwargs['user']
    user_id = str(current_user['id'])
    user = get_object_or_404(models.UserStorage, pk=user_id)
    if request.method == 'POST':
        # create FORM
        form = make_CreateDetectorForm(user_id, user_sid, request.POST)

        if form.is_valid():
            detector_project = form.data.get('detector_project')
            detector_localization = form.data.get('detector_localization')
            detector_coordinates_x = form.data.get('detector_coordinates_x')
            detector_coordinates_y = form.data.get('detector_coordinates_y')
            detector_finder = form.data.get('detector_finder')
            detector_find_date = form.data.get('detector_find_date')
            detector_circumstances = form.data.get('detector_circumstances')
            detector_depth = form.data.get('detector_depth')
            detector_dating = form.data.get('detector_dating')
            detector_exact_dating = form.data.get('detector_exact_dating')
            detector_kind = form.data.get('detector_kind')
            detector_material = form.data.get('detector_material')
            detector_quantity = form.data.get('detector_quantity')
            detector_note = form.data.get('detector_note')
            detector_organisation_passed = form.data.get('detector_organisation_passed')
            detector_evidence_number = form.data.get('detector_evidence_number')
            detector_find_passed = form.data.get('detector_find_passed')
            detector_accessibility = form.data.get('detector_accessibility')

            params = {}
            if (detector_project):
                params['projekt'] = str(detector_project)
            if (detector_localization):
                params['lokalizace'] = str(detector_localization)
            params['katastr'] = '-1'
            if (detector_coordinates_x and detector_coordinates_y):
                params['zswgs'] = str(detector_coordinates_x)
                params['zdwgs'] = str(detector_coordinates_y)
            if (detector_finder):
                params['nalezce'] = str(detector_finder)
            if (detector_find_date):
                params['datum_nalezu'] = helper_doc.date_to_psql_date(str(detector_find_date))
            else:
                params['datum_nalezu'] = '__NULL__'
            if (detector_circumstances):
                params['okolnosti'] = str(detector_circumstances)
            else:
                params['okolnosti'] = '__NULL__'
            if (detector_depth):
                params['hloubka'] = str(detector_depth)
            if (detector_dating):
                params['obdobi'] = str(detector_dating)
            else:
                params['obdobi'] = '__NULL__'
            if (detector_exact_dating):
                params['presna_datace'] = str(detector_exact_dating)
            if (detector_kind):
                params['druh_nalezu'] = str(detector_kind)
            else:
                params['druh_nalezu'] = '__NULL__'
            if (detector_material):
                params['specifikace'] = str(detector_material)
            else:
                params['specifikace'] = '__NULL__'
            if (detector_quantity):
                params['pocet'] = str(detector_quantity)
            if (detector_note):
                params['poznamka'] = str(detector_note)
            if (detector_organisation_passed):
                params['predano_organizace'] = str(detector_organisation_passed)
            if (detector_evidence_number):
                params['inv_cislo'] = str(detector_evidence_number)
            if (detector_find_passed):
                if str(detector_find_passed) == 'True':
                    params['predano'] = 'true'
                else:
                    params['predano'] = 'false'
            if (detector_accessibility):
                params['pristupnost'] = str(detector_accessibility)

            if(ident_cely == '0'):
                # I am creating the object
                ret = helper_det.zapsani(params, user, user_sid)

                if ret:
                    ident_cely = ret.ident_cely
                    messages.add_message(request, messages.SUCCESS, c.OBJECT_CREATED_SUCCESSFULLY)
                else:
                    ident_cely = ''
                    logger.error("Nepovedlo se vytvorit samostatny nalez")
                    messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_CREATED)
            else:
                params['ident_cely'] = ident_cely
                nalez = models.SamostatnyNalez.objects.get(ident_cely=ident_cely)
                params['id'] = nalez.id
                params['stav'] = nalez.stav

                if 'button_save' in request.POST:
                    ret = helper_det.update(params, nalez, user, user_sid)
                elif 'button_send_to_confirm' in request.POST:
                    ret = helper_det.odeslani(params, nalez, user, user_sid)
                elif 'button_confirm' in request.POST:
                    ret = helper_det.potvrzeni(params, nalez, user, user_sid)
                elif 'button_archive' in request.POST:
                    ret = helper_det.archivace(params, nalez, user, user_sid)
                else:
                    logger.debug("Unknown post request button type")

                if 'button_delete' in request.POST:
                    resp = nalez.delete()
                    if resp[0] > 0:
                        logger.debug("Objekt " + str(resp) + ' smazán')
                        messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)
                        return redirect('/pas/create/')
                    else:
                        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_DELETED)

            return redirect('/pas/create/' + ident_cely)

        logger.warning('Form create is not valid')
        logger.warning(form.errors)
        logger.warning(form.non_field_errors)
        return render(request, 'detectors/create.html', {'formDetCreate': form})

    elif request.method == 'GET':
        addNameForm = AddNameForm()
        context = {}
        if(ident_cely == '0'):
            formDetCreate = make_CreateDetectorForm(user_id, user_sid, initial={
                'detector_find_passed': False,
                'detector_finder': str(connector.get_id_name_by_user_id(user_id)),
                'detector_accessibility': 3, # Admin
            }, editProject=True)
            context['showFiles'] = 'False'
            context['archivovano'] = False

        else:
            # Detail
            context['showFiles'] = 'True'
            nalez = get_object_or_404(models.SamostatnyNalez, ident_cely=ident_cely)
            context['archivovano'] = True if  nalez.stav == det_const.ARCHIVOVANY else False
            id_nalez = nalez.id
            resp = xmlrpc.nacti_informace_list(user_sid, 'detektor', [id_nalez])
            db_param = resp[0]['0']
            coor = db_param['geom'].replace(")", "").replace("POINT(", "").split(" ")
            #print(db_param)
            userArchive = get_object_or_404(models.UserStorage, pk=db_param['odpovedny_pracovnik_archivace'])
            # Now assuming id of the organisation is the same as id of the atree object
            orgArch = get_object_or_404(models.Organizace, pk=userArchive.organizace.id)
            userAdded = get_object_or_404(models.UserStorage, pk=db_param['odpovedny_pracovnik_vlozeni'])
            orgAdd = get_object_or_404(models.Organizace, pk=userAdded.organizace.id)
            if len(coor) == 1:
                coor = ['', '']

            param = {
                'detector_project': db_param['projekt'],
                'detector_localization': db_param['lokalizace'],
                'detector_coordinates_x': coor[1],
                'detector_coordinates_y': coor[0],
                'detector_finder': db_param['nalezce'],
                'detector_find_date': helper_doc.date_from_psql_date(db_param['datum_nalezu']),
                'detector_circumstances': db_param['okolnosti'],
                'detector_depth': db_param['hloubka'],
                'detector_dating': db_param['obdobi'],
                'detector_exact_dating': db_param['presna_datace'],
                'detector_kind': db_param['druh_nalezu'],
                'detector_material': db_param['specifikace'],
                'detector_quantity': db_param['pocet'],
                'detector_note': db_param['poznamka'],
                'detector_organisation_passed': db_param['predano_organizace'],
                'detector_find_passed': False if db_param['predano'] == 'f' else db_param['predano'],
                'detector_evidence_number': '' if db_param['inv_cislo'] == '-1' else db_param['inv_cislo'],
                'detector_accessibility': db_param['pristupnost']
            }

            try:
                if db_param['katastr'] != '-1':
                    param['detector_cadastry'] = c.CADASTRY_DICT[int(db_param['katastr'])]
            except KeyError:
                logger.debug("Unknown cataster id: " + db_param['katastr'])

            projekt_id = db_param['projekt']
            soubory = models.Soubor.objects.filter(samostatny_nalez=id_nalez)
            context['soubory'] = soubory
            if (not resp[0]):
                raise Http404()
            formDetCreate = make_CreateDetectorForm(user_id, user_sid, initial=param)

    curr_role = helper_doc.get_roles_and_permissions(current_user['auth'])['role']
    if(ident_cely == '0'):
        return render(request, 'detectors/create.html', {
            'canEdit': True,
            'canConfirm': False,
            'canArchive': False,
            'canUnarchive': False,
            'canProject': True,
            'smStav': 0,
            'ident_cely': '0',
            'projectId': 's',
            'addNameForm': addNameForm,
            'formDetCreate': formDetCreate,
            'context': context})

    # print("---+++++++++++++++++----")
    # print("user = "+str(curr_user['id']))
    # print("role = "+curr_role)
    # print("organizace = "+str(curr_user['organizace']))
    # print("SM stav = "+db_param['stav'])
    # print("SM nalezce = "+str(db_param['nalezce']))
    # print("SM organizace = "+str(db_param['predano_organizace']))

    # detector state in header
    detStav = int(db_param['stav'])
    states_dict = dict(det_const.DETECTOR_STATE_CACHE)
    currentStav = states_dict[detStav]
    isOwner = str(db_param['odpovedny_pracovnik_vlozeni']) == str(current_user['id'])
    isFromOrganisation = str(db_param['predano_organizace']) == str(current_user['organizace'])
    isBadatel = curr_role == c.BADATEL
    isArcheolog = curr_role == c.ARCHEOLOG
    isArchivar = curr_role == c.ARCHIVAR
    isAdmin = curr_role == c.ADMIN

    if (str(db_param['stav']) == str(det_const.ZAPSANY) and isOwner) or (str(db_param['stav']) != str(det_const.ARCHIVOVANY) and (isArchivar or isAdmin)):
        canEdit = True
    else:
        canEdit = False

    if (str(db_param['stav']) == str(det_const.ODESLANY) and curr_role == 'Archeolog' and isFromOrganisation) or (str(db_param['stav']) != str(det_const.ARCHIVOVANY) and curr_role in ['Archivář', 'Admin']):
        canConfirm = True
    else:
        canConfirm = False

    if str(db_param['stav']) == str(det_const.POTVRZENY) and curr_role in ['Archivář', 'Admin']:
        canArchive = True
    else:
        canArchive = False
    if str(db_param['stav']) == str(det_const.ARCHIVOVANY) and curr_role in ['Archivář', 'Admin']:
        canUnarchive = True
    else:
        canUnarchive = False

    canSeeDetail = (isOwner and isBadatel) or (isArcheolog and isFromOrganisation) or isArchivar or isAdmin
    #print("canEdit= "+str(canEdit));
    #print("canConfirm= "+str(canConfirm));
    #print("canArchive= "+str(canArchive));

    if canSeeDetail:
        return render(request, 'detectors/create.html', {
            'canEdit': canEdit,      # Pokud jsem vlastnikem
            'canConfirm': canConfirm,  # pokud jsem archeol & mam stejnou organizaci jako SN
            'canArchive': canArchive,  # pokud jsem archiv
            'canUnarchive': canUnarchive,
            'canProject': True if ident_cely == '0' else False,
            'smStav': int(db_param['stav']),
            'currentStav': currentStav,
            'ident_cely': ident_cely,
            'projectId': projekt_id,
            'addNameForm': addNameForm,
            'formDetCreate': formDetCreate,
            'context': context})
    else:
        return render(request, '403.html')


@min_user_group(c.ARCHEOLOG)
def return_finding(request, ident_cely, **kwargs):
    current_user = kwargs['user']
    nalez = get_object_or_404(models.SamostatnyNalez, ident_cely=ident_cely)
    stavy = dict(det_const.DETECTOR_STATE_CACHE)
    user_id = str(current_user['id'])
    user = get_object_or_404(models.UserStorage, pk=user_id)

    if (nalez.stav != det_const.ODESLANY) and (nalez.stav != det_const.POTVRZENY) and (nalez.stav != det_const.ARCHIVOVANY):
        print("Nepovoleny stav vraceni: " + str(nalez.stav) + " Povolene stavy: " + str(det_const.ODESLANY) + ", " + str(det_const.POTVRZENY)) + ", " + str(det_const.ARCHIVOVANY)
        return render(request, '403.html')

    stary_stav = stavy[nalez.stav]
    novy_stav = stavy[nalez.stav - 1]

    if request.method == 'POST':
        form = ReturnFindingForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data['reason']
            if nalez.stav == det_const.ODESLANY:
                ret = helper_det.vraceni_k_odeslani(user, nalez, reason)
            if nalez.stav == det_const.POTVRZENY:
                ret = helper_det.vraceni_k_potvrzeni(user, nalez, reason)
            if nalez.stav == det_const.ARCHIVOVANY:
                ret = helper_det.vraceni_k_archivaci(user, nalez, reason)

            response = redirect('/pas/create/' + ident_cely)
        else:
            logger.debug("Form is not valid")
            response = render(request, 'detectors/vrat_nalez.html', {'form': form})
    else:
        form = ReturnFindingForm()

        response = render(request, 'detectors/vrat_nalez.html', {
            'form': form,
            'nalez': nalez,
            'old_state': stary_stav,
            'new_state': novy_stav
        })

    return response


def table_view(request, params_dict):
    detektors = connector.detector(request, params_dict)
    language = translation.get_language()

    docArray = []
    NAME_CACHE = dict(helper_doc.load_name_cache())
    organizace = heslar_organizace()
    predmet_druhy = HeslarPredmetDruh.objects.all()
    odbodi_druha = HeslarObdobiDruha.objects.all()
    specofikace_druha = HeslarSpecifikacePredmetu.objects.all()

    for det in detektors:
        f_data = det['0']
        try:
            for i in det_const.DETECTOR_STATE_CACHE:
                if i[0] == int(f_data['stav']):
                    f_data['stav'] = 'N' + f_data['stav'] + ' (' + str(i[1]) + ')'
                    break
        except Exception as ex:
            logger.warning(ex)
            f_data['stav'] = ''
        try:
            f_data['nalezce'] = NAME_CACHE[int(f_data['nalezce'])]
        except:
            logger.debug("Could not map finder to name")
            f_data['nalezce'] = ''
        try:
            for druh in predmet_druhy:
                if druh.id == int(f_data['druh_nalezu']):
                    if language == 'cs':
                        f_data['druh_nalezu'] = druh.nazev
                    elif language == 'en':
                        f_data['druh_nalezu'] = druh.en
                    break
        except:
            f_data['druh_nalezu'] = ''
        try:
            for spec in specofikace_druha:
                if spec.id == int(f_data['specifikace']):
                    if language == 'cs':
                        f_data['specifikace'] = spec.nazev
                    elif language == 'en':
                        f_data['specifikace'] = spec.en
                    break
        except:
            f_data['specifikace'] = ''
        try:
            for obdobi in odbodi_druha:
                if obdobi.id == int(f_data['obdobi']):
                    if language == 'cs':
                        f_data['obdobi'] = obdobi.nazev
                    elif language == 'en':
                        f_data['obdobi'] = obdobi.en
                    break
        except:
            f_data['obdobi'] = ''
        try:
            for o in organizace:
                if o[0] == int(f_data['predano_organizace']):
                    f_data['predano_organizace'] = o[1]
                    break
        except:
            f_data['predano_organizace'] = ''

        if f_data['predano'] == 't':
            f_data['predano'] = _('Ano')
        else:
            f_data['predano'] = _('Ne')

        if f_data['inv_cislo'] == '-1':
            f_data['inv_cislo'] = ''
        try:
            if f_data['datum_vlozeni'] != '-1':
                f_data['datum_vlozeni'] = helper_doc.epoch_timestamp_to_datetime(int(f_data['datum_vlozeni']))
            else:
                f_data['datum_vlozeni'] = ''
        except:
            f_data['datum_vlozeni'] = ''
        try:
            if f_data['datum_archivace'] != '-1':
                f_data['datum_archivace'] = helper_doc.epoch_timestamp_to_datetime(int(f_data['datum_archivace']))
            else:
                f_data['datum_archivace'] = ''
        except:
            f_data['datum_archivace'] = ''

        try:
            kat_id = int(f_data['katastr'])
            cadastre_index = [x[0] for x in c.CADASTRE_12_CACHE].index(kat_id)
            kataster = c.CADASTRE_12_CACHE[cadastre_index][1]
            f_data['katastr'] = kataster[:kataster.index('(') - 1]
            f_data['okres'] = kataster[kataster.index('(') + 1:kataster.index(')')]
        except:
            f_data['katastr'] = ''
            f_data['okres'] = ''

        docArray.append(f_data)
    return docArray


@min_user_group(c.BADATEL)
def my_detectors(request, **kwargs):
    params_dict = {
        'odpovedny_pracovnik_vlozeni': str(kwargs['user']['id'])
    }
    docArray = table_view(request, params_dict)

    return render(request, 'detectors/moje.html', {'table': docArray})


@min_user_group(c.BADATEL)
def choose(request, **kwargs):
    user_sid = request.COOKIES.get('sessionId')
    curr_user = kwargs['user']
    user_id = str(curr_user['id'])
    if request.method == 'POST':
        form = make_ChooseDetectorForm(user_id, user_sid, request.POST)
        if form.is_valid():
            detector_project_id = form.data.get('detector_project_id')
            detector_finding_id = form.data.get('detector_finding_id')
            detector_process_state = form.data.get('detector_process_state')
            detector_region = form.data.get('detector_region')
            detector_district = form.data.get('detector_district')
            detector_finder = form.data.get('detector_finder')
            detector_date_of_change_from = form.data.get('detector_date_of_change_from')
            detector_date_of_change_to = form.data.get('detector_date_of_change_to')
            detector_find_date_from = form.data.get('detector_find_date_from')
            detector_find_date_to = form.data.get('detector_find_date_to')
            detector_description_details = form.data.get('detector_description_details')
            detector_dating = form.data.get('detector_dating')
            detector_kind = form.data.get('detector_kind')
            detector_material = form.data.get('detector_material')
            detector_organisation = form.data.get('detector_organisation')
            detector_project_leader = form.data.get('detector_project_leader')
            detector_evidence_number = form.data.get('detector_evidence_number')
            detector_find_passed = form.data.get('detector_find_passed')
            detector_accessibility = form.data.get('detector_accessibility')

            params = {}
            params['stav'] = '-1'
            params['predano'] = '-1'
            # Parameters retrieved from the form that are non are ignored
            if (detector_project_id):
                params['projekt_ident'] = str(detector_project_id)
            if (detector_finding_id):
                params['ident_cely'] = str(detector_finding_id)
            if (detector_process_state):
                params['stav'] = str(detector_process_state)
            if (detector_region):
                params['region'] = str(detector_region)
            if (detector_district):
                params['okres'] = str(detector_district)
            if (detector_finder):
                params['nalezce'] = str(detector_finder)
            if (detector_date_of_change_from):
                params['datum_zmeny_od'] = helper_doc.date_to_psql_date(str(detector_date_of_change_from))
            if (detector_date_of_change_to):
                params['datum_zmeny_do'] = helper_doc.date_to_psql_date(str(detector_date_of_change_to))
            if (detector_find_date_from):
                params['datum_nalezu_od'] = str(detector_find_date_from)
            if (detector_find_date_to):
                params['datum_nalezu_do'] = str(detector_find_date_to)
            if (detector_description_details):
                params['popis'] = str(detector_description_details)
            if (detector_dating):
                params['obdobi'] = str(detector_dating)
            if (detector_kind):
                params['druh_nalezu'] = str(detector_kind)
            if (detector_material):
                params['specifikace'] = str(detector_material)
            if (detector_organisation):
                params['predano_organizace'] = str(detector_organisation)
            if (detector_project_leader):
                params['projekt_vedouci'] = str(detector_project_leader)
            if (detector_evidence_number):
                params['inv_cislo'] = str(detector_evidence_number)
            if (detector_find_passed):
                if str(detector_find_passed) == 'True':
                    params['predano'] = 'true'
                elif str(detector_find_passed) == 'False':
                    params['predano'] = 'false'
            if (detector_accessibility):
                params['pristupnost'] = str(detector_accessibility)
            curr_role = helper_doc.get_roles_and_permissions(curr_user['auth'])['role']
            if curr_role in ['Badatel']:
                params['odpovedny_pracovnik_vlozeni'] = str(curr_user['id'])
            elif curr_role in ['Archeolog']:
                params['predano_organizace'] = str(curr_user['organizace'])

            docArray = table_view(request, params)
            return render(request, 'detectors/list.html', {'table': docArray})

        print('Form is not valid')
        print(form.errors)

    else:
        formChoose = make_ChooseDetectorForm(user_id, user_sid, initial={})
    return render(request, 'detectors/choose.html', {'formChoose': formChoose})


@min_user_group(c.BADATEL)
def cooperate(request, **kwargs):
    context = {}

    user = kwargs['user']
    curr_role = helper_doc.get_roles_and_permissions(user['auth'])['role']
    if(curr_role == "Admin"):
        context['canDelete'] = True
    else:
        context['canDelete'] = False

    spolupraceQ = models.VazbaSpoluprace.objects.all()
    organizaceQ = models.Organizace.objects.values_list('id', 'nazev_zkraceny', named=True)

    if curr_role in ('Badatel', 'Archeolog'):
        spolupraceQ = spolupraceQ.filter(Q(badatel=user['id']) | Q(archeolog=user['id']))
    spoluprace = spolupraceQ.values(
        'id',
        'badatel',
        'archeolog',
        'aktivni',
        'potvrzeno',
        'datum_vytvoreni'
    )

    for s in spoluprace:
        badatel = models.UserStorage.objects.get(pk=s['badatel'])
        archeolog = models.UserStorage.objects.get(pk=s['archeolog'])
        badatelOrg = organizaceQ.get(pk=badatel.organizace.id)
        archeologOrg = organizaceQ.get(pk=archeolog.organizace.id)
        s['badatel'] = badatel.prijmeni + ', ' + badatel.jmeno
        s['badatel_organizace'] = badatelOrg.nazev_zkraceny
        s['badatel_email'] = badatel.email
        s['archeolog'] = archeolog.prijmeni + ', ' + archeolog.jmeno
        s['archeolog_organizace'] = archeologOrg.nazev_zkraceny
        s['archeolog_email'] = archeolog.email
        s['aktivni'] = c.BOOL_DICT[s['aktivni']]
        s['potvrzeno'] = c.BOOL_DICT[s['potvrzeno']]
        s['badatel_ident'] = badatel.ident_cely
        s['archeolog_ident'] = archeolog.ident_cely
        s['datum_vytvoreni'] = helper_doc.epoch_timestamp_to_datetime(s['datum_vytvoreni'])
        s['zmena_potvrzeni'] = models.HistorieSpoluprace.objects.filter(
            vazba_spoluprace=s['id'],
            typ_zmeny=det_const.SPOLUPRACE_POTVRZENI).order_by('datum_zmeny').last()

    context['spoluprace'] = spoluprace

    return render(request, 'detectors/cooperate.html', {'context': context})


@min_user_group(c.ARCHEOLOG)
def confirm(request, **kwargs):
    curr_user = kwargs['user']
    curr_role = helper_doc.get_roles_and_permissions(curr_user['auth'])['role']
    params_dict = {'stav': '2', 'predano_organizace': str(curr_user['organizace'])}
    docArray = []
    if curr_role in ['Archeolog', 'Archivář', 'Admin']:
        docArray = table_view(request, params_dict)

    return render(request, 'detectors/confirm.html', {'table': docArray})


@min_user_group(c.ARCHIVAR)
def archive(request, **kwargs):
    curr_user = kwargs['user']
    curr_role = helper_doc.get_roles_and_permissions(curr_user['auth'])['role']
    params_dict = {'stav': '3'}
    docArray = []
    if curr_role in ['Archivář', 'Admin']:
        docArray = table_view(request, params_dict)

    return render(request, 'detectors/archive.html', {'table': docArray})


@min_user_group(c.BADATEL)
def createCooperation(request, **kwargs):

    sid = request.COOKIES.get('sessionId')
    context = {}
    context['errors'] = []

    if request.method == 'POST':
        newCooperationForm = CreateCooperateForm(request.POST)
        if newCooperationForm.is_valid():
            archeolog_email = newCooperationForm.data.get('archeolog')
            id_archeo = helper_doc.get_archeologist_id(sid, archeolog_email)
            userId = helper_doc.get_logged_user_id(sid)

            user = get_object_or_404(models.UserStorage, pk=userId)
            archeo = get_object_or_404(models.UserStorage, pk=id_archeo)
            cas = helper_doc.getCurrentEpochTime()
            doesNotExist = models.VazbaSpoluprace.objects.filter(archeolog=id_archeo, badatel=userId).count() == 0

            if id_archeo == -1:
                context['errors'].append(('archeologNotFound', 'Archeolog s emailem ' + archeolog_email + ' nenalezen'))
            elif id_archeo == userId:
                context['errors'].append(('cantRealteToMe', 'Nelze vytvořit spolupráci sám se sebou'))
            elif not doesNotExist:
                context['errors'].append(
                    ('cooperationExists', "Spolupráce s archeologem s emailem " + archeolog_email + " již existuje."))
            else:
                s = models.VazbaSpoluprace(
                    archeolog=archeo,
                    badatel=user,
                    aktivni=False,
                    potvrzeno=False,
                    datum_vytvoreni=cas)
                s.save()

                # Log zmen spolupráce, zádost
                zmena = models.HistorieSpoluprace(
                    typ_zmeny=det_const.SPOLUPRACE_ZADOST,
                    vazba_spoluprace=s,
                    uzivatel=user
                )
                zmena.save()

                messages.add_message(request, messages.SUCCESS, c.COOPERATION_REQUESTED)
                amcemails.email_send_SN5.delay(request.META['HTTP_HOST'], user, archeo.email, s)

                return redirect('pas:cooperate')

        else:
            print("Form is no valid")
            context['errors'].append(('invalidForm', "Nesprávný formát emailu."))

    else:
        newCooperationForm = CreateCooperateForm()

    return render(request, 'detectors/vazbaSpoluprace_create_form.html', {
        'newCooperationForm': newCooperationForm,
        'context': context
    })


@login_required
def updateCooperation(request, pk, **kwargs):

    if request.method == 'POST':
        form = UpdateCooperateForm(request.POST)
        spoluprace = get_object_or_404(models.VazbaSpoluprace, pk=pk)

        potvrzuji = False
        aktivuji = False
        deaktivuji = False

        if form.is_valid():
            aktivni = form.cleaned_data['aktivni']
            potvrzeno = form.cleaned_data['potvrzeno']

            sid = request.COOKIES.get('sessionId')
            userId = helper_doc.get_logged_user_id(sid)
            user = get_object_or_404(models.UserStorage, pk=userId)

            if spoluprace.aktivni and not aktivni:
                deaktivuji = True
            elif not spoluprace.aktivni and aktivni:
                aktivuji = True
            elif not spoluprace.potvrzeno and potvrzeno:
                potvrzuji = True

            if aktivuji:
                # aktivace
                spoluprace.aktivni = True
                zmena = models.HistorieSpoluprace(
                    typ_zmeny=det_const.SPOLUPRACE_AKTIVACE,
                    vazba_spoluprace=spoluprace,
                    uzivatel=user
                )
                zmena.save()
                messages.add_message(request, messages.SUCCESS, c.COOPERATION_ACTIVATED)
            elif deaktivuji:
                spoluprace.aktivni = False
                zmena = models.HistorieSpoluprace(
                    typ_zmeny=det_const.SPOLUPRACE_DEAKTIVACE,
                    vazba_spoluprace=spoluprace,
                    uzivatel=user
                )
                zmena.save()
                messages.add_message(request, messages.SUCCESS, c.COOPERATION_DEACTIVATED)
            elif potvrzuji:
                # potvrzení
                spoluprace.aktivni = True
                spoluprace.potvrzeno = True
                zmena = models.HistorieSpoluprace(
                    typ_zmeny=det_const.SPOLUPRACE_POTVRZENI,
                    vazba_spoluprace=spoluprace,
                    uzivatel=user
                )
                zmena.save()
                messages.add_message(request, messages.SUCCESS, c.COOPERATION_APPROVED)
            else:


                target_email = spoluprace.badatel.email
                amcemails.email_send_SN7.delay(user, target_email)

            spoluprace.save()

        else:
            print('Form is not valid')

        return redirect('pas:cooperate')

    spoluprace = get_object_or_404(models.VazbaSpoluprace, pk=pk)
    form = UpdateCooperateForm({
        'aktivni': spoluprace.aktivni,
        'potvrzeno': spoluprace.potvrzeno
    })

    badatel_name = helper_general.get_user_name_from_id(spoluprace.badatel.id)
    archeolog_name = helper_general.get_user_name_from_id(spoluprace.archeolog.id)

    context = {
        'nepotvrzeno': not spoluprace.potvrzeno,
        'aktivni_spoluprace': spoluprace.aktivni,
        'spoluprace': spoluprace,
        'badatel_name': badatel_name,
        'archeolog_name': archeolog_name,
        'archeolog_id': spoluprace.archeolog.id.id,
        'badatel_id': spoluprace.badatel.id.id
    }

    return render(request, 'detectors/vazbaSpoluprace_update_form.html', {'form': form, 'context': context})


@min_user_group(c.ADMIN)
def deleteCooperation(request, pk, **kwargs):

    deleted = models.VazbaSpoluprace.objects.filter(pk=pk).delete()

    if(deleted[0] > 0):
        logger.debug("Deleted spoluprace object with id: " + str(pk) + ", " + str(deleted))
        messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)
    else:
        logger.debug("Could not find spoluprace object with id " + str(pk))
        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_DELETED)

    return redirect('pas:cooperate')


def historyCooperationList(request, pk):

    historie = models.HistorieSpoluprace.objects.filter(vazba_spoluprace__id=pk)

    return render(request, 'detectors/history_spoluprace.html', {'historie': historie})


def historyDetectorsList(request, ident_cely):

    nalez = models.SamostatnyNalez.objects.get(ident_cely=ident_cely)
    historie = models.HistorieSamNalezu.objects.filter(samostatny_nalez=nalez)

    return render(request, 'detectors/history_detectors.html', {
        'historie': historie,
        'ident_cely': ident_cely
    })
