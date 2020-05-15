from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Q
from django.db import IntegrityError

from . import xmlrpc
from . import helper
from .constants import AmcrConstants as c
from .decorators import login_required, min_user_group
from .forms import (FindingDocumentForm, AddNameForm, ChooseForm, CreateForm, LoginForm, EditAuthorForm)
from .models import (HeslarObjektDruh, HeslarPredmetDruh, HeslarTypNalezu, Dokument, HistorieDokumentu,
                     KomponentaDokument, HeslarObdobiDruha, HeslarArealDruha, NalezDokument, UserStorage,
                     ExtraData, JednotkaDokument, HeslarZeme)
from detectors.models import HeslarJmena
from detectors.forms import ReturnFindingForm

import logging
import ftplib
import mimetypes
from datetime import datetime
from shapely import wkb


logger = logging.getLogger(__name__)

PREDMET_OPTION = 2
OBJEKT_OPTION = 1


@login_required
def upload_file(request, pk, **kwargs):

    context = {}
    sid = request.COOKIES.get('sessionId')
    dokument = Dokument.objects.get(pk=pk)
    context['ident_cely'] = dokument.ident_cely
    context['documentId'] = pk

    if request.method == 'POST' and request.FILES['myFile']:
        uploadedFile = request.FILES['myFile']

        try:
            xmlrpc.uploadDocumentFile(sid, dokument, uploadedFile)
            messages.add_message(request, messages.SUCCESS, c.FILE_UPLOADED_SUCCESSFULLY)
        except Exception as ex:
            logger.debug('Chyba pri uploadu souboru: ' + str(ex))
            messages.add_message(request, messages.WARNING, c.FILE_COULD_NOT_BE_UPLOADED)

        response = redirect('/documents/create/' + dokument.ident_cely)
    else:
        response = render(request, 'documents/uploadFile.html', {'context': context})

    return response


@login_required
def download_file(request, pk, **kwargs):

    sid = request.COOKIES.get('sessionId')
    try:
        name, f = xmlrpc.downloadFile(sid, pk)
        content_type = mimetypes.guess_type(name)[0]  # Use mimetypes to get file type
        f.seek(0)
        data = f.read()
        response = HttpResponse(data, content_type=content_type)
        response['Content-Length'] = str(len(data))
        response['Content-Disposition'] = "attachment; filename=%s" % name
        f.close()
    except (ftplib.all_errors, Exception):
        logger.debug('Chyba pri stahovani souboru')
        messages.add_message(request, messages.WARNING, c.FILE_COULD_NOT_BE_DOWNLOADED)
    else:
        return response


@login_required
def finding_update(request, pk, **kwargs):

    context = {}
    nalez = get_object_or_404(NalezDokument, pk=pk)
    ident_cely_dokument = nalez.komponenta_dokument.jednotka_dokument.dokument.ident_cely
    context['ident_cely'] = ident_cely_dokument
    context['detail'] = True

    if request.method == 'POST':
        form = FindingDocumentForm(request.POST)
        if form.is_valid():
            typ_nalezu_id = form.cleaned_data['typ_nalezu']
            druh_objektu_id = form.cleaned_data['druh_objektu']
            druh_predmetu_id = form.cleaned_data['druh_predmetu']
            specifikace_objektu_id = form.cleaned_data['specifikace_objektu']
            specifikace_predmetu_id = form.cleaned_data['specifikace_predmetu']
            poznamka = form.cleaned_data['poznamka']
            pocet = form.cleaned_data['pocet']

            if typ_nalezu_id:
                nalez.typ_nalezu = HeslarTypNalezu.objects.get(pk=typ_nalezu_id)
            if typ_nalezu_id == str(PREDMET_OPTION):
                nalez.druh_nalezu = druh_predmetu_id
                nalez.specifikace = specifikace_predmetu_id
            elif typ_nalezu_id == str(OBJEKT_OPTION):
                nalez.druh_nalezu = druh_objektu_id
                nalez.specifikace = specifikace_objektu_id
            else:
                logger.debug("Neznamy typ nelezu: " + str(typ_nalezu_id) + " <> " +
                             str(PREDMET_OPTION) + "/" + str(OBJEKT_OPTION))

            nalez.poznamka = poznamka
            nalez.pocet = pocet
            nalez.save()

            response = redirect('/documents/create/' + nalez.komponenta_dokument.jednotka_dokument.dokument.ident_cely)

        else:
            logger.debug("Form is not valid")
            logger.debug(form.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)
    else:

        form_data = {
            'typ_nalezu': nalez.typ_nalezu.id,
            'poznamka': nalez.poznamka,
            'pocet': nalez.pocet,
        }
        if nalez.typ_nalezu.id == PREDMET_OPTION:
            form_data['druh_predmetu'] = nalez.druh_nalezu
            form_data['specifikace_predmetu'] = nalez.specifikace
        else:
            form_data['druh_objektu'] = nalez.druh_nalezu
            form_data['specifikace_objektu'] = nalez.specifikace

        form = FindingDocumentForm(initial=form_data)

        response = render(request, 'documents/finding.html', {
            'form': form,
            'context': context,
        })

    return response


@login_required
def finding_create(request, ident_cely, **kwargs):

    context = {}
    komponenta = get_object_or_404(KomponentaDokument, ident_cely=ident_cely)
    ident_cely_dokument = komponenta.jednotka_dokument.dokument.ident_cely
    context['ident_cely'] = ident_cely_dokument

    if request.method == 'POST':
        form = FindingDocumentForm(request.POST)
        if form.is_valid():
            typ_nalezu_id = form.cleaned_data['typ_nalezu']
            druh_objektu_id = form.cleaned_data['druh_objektu']
            druh_predmetu_id = form.cleaned_data['druh_predmetu']
            specifikace_objektu_id = form.cleaned_data['specifikace_objektu']
            specifikace_predmetu_id = form.cleaned_data['specifikace_predmetu']
            poznamka = form.cleaned_data['poznamka']
            pocet = form.cleaned_data['pocet']

            nalez = NalezDokument()

            if typ_nalezu_id:
                nalez.typ_nalezu = HeslarTypNalezu.objects.get(pk=typ_nalezu_id)
            if typ_nalezu_id == str(PREDMET_OPTION):
                nalez.druh_nalezu = druh_predmetu_id
                if specifikace_predmetu_id:
                    nalez.specifikace = specifikace_predmetu_id
            elif typ_nalezu_id == str(OBJEKT_OPTION):
                nalez.druh_nalezu = druh_objektu_id
                if specifikace_objektu_id:
                    nalez.specifikace = specifikace_objektu_id

            nalez.komponenta_dokument = komponenta
            nalez.poznamka = poznamka
            nalez.pocet = pocet
            nalez.save()
            logger.debug("Created finding: " + str(nalez.__dict__))
            messages.add_message(request, messages.SUCCESS, c.OBJECT_CREATED_SUCCESSFULLY)

            # redirect to create document
            response = redirect('/documents/create/' + ident_cely_dokument)

        else:
            logger.debug("Form is not valid")
            logger.debug(form.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)
    else:

        form = FindingDocumentForm()
        response = render(request, 'documents/finding.html', {
            'form': form,
            'context': context,
        })

    return response

# user is admin


@login_required
def finding_delete(request, pk, **kwargs):

    nalez = NalezDokument.objects.get(pk=pk)
    ident_cely_dokument = nalez.komponenta_dokument.jednotka_dokument.dokument.ident_cely
    deleted = nalez.delete()

    if(deleted[0] > 0):
        logger.debug("Deleted finding object with id: " + str(pk) + ", " + str(deleted))
        messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)
    else:
        logger.debug("Could not find document finding object with id " + str(pk))
        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_DELETED)

    return redirect('/documents/create/' + ident_cely_dokument)


@login_required
def name_create(request, **kwargs):

    if request.method == 'POST':
        form = AddNameForm(request.POST)
        if form.is_valid():

            j = form.cleaned_data['jmeno']
            prijmeni = form.cleaned_data['prijmeni']

            try:
                jmeno = HeslarJmena(
                    jmeno=j,
                    prijmeni=prijmeni,
                    validated=True,
                    vypis=prijmeni + ', ' + j[0].upper() + '.',
                    vypis_cely=prijmeni + ', ' + j
                )
                jmeno.save()

                logger.debug("Nove jmeno pridano do heslare: " + jmeno.vypis)
                # Add message to the user
                messages.add_message(request, messages.SUCCESS, c.NAME_ADDED_TO_THE_LIST)
            except IntegrityError as ex:
                logger.debug(str(ex))
                messages.add_message(request, messages.WARNING, c.NAME_ALREADY_EXISTS)

            # redirect to the author edit form
            response = redirect(request.META['HTTP_REFERER'])
        else:
            logger.debug("Form is not valid.")
            logger.debug(form.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)
    else:
        response = JsonResponse(-1, safe=False)

    return response


@login_required
def author_edit(request, ident_cely, **kwargs):

    MAX_AUTHOR_COUNT = 4
    sid = request.COOKIES.get('sessionId')
    addNameForm = AddNameForm()
    names = xmlrpc.get_list(sid, 'jmena', 'prijmeni', 'jmeno')
    dokument = get_object_or_404(Dokument, ident_cely=ident_cely)

    if request.method == 'POST':
        editAuthorForm = EditAuthorForm(request.POST, names=[('', '----')] + names)

        current_user = kwargs['user']
        user = get_object_or_404(UserStorage, pk=current_user['id'])

        if editAuthorForm.is_valid():
            data = editAuthorForm.cleaned_data
            autori_ids = []
            print(str(data))
            for i in range(MAX_AUTHOR_COUNT):
                author = data['author' + str(i + 1)]
                if author:
                    autori_ids.append(author)

            authors_str = 'Nezadán'
            first = True
            for autor_id in autori_ids:
                if autor_id:
                    autor = get_object_or_404(HeslarJmena, pk=autor_id)
                    if first:
                        authors_str = ''
                        authors_str += autor.vypis_cely
                        first = False
                    else:
                        authors_str += ';' + autor.vypis_cely
            dokument.autor = authors_str
            dokument.save()

            zmena = HistorieDokumentu(
                typ_zmeny=c.ZMENA_AUTORA,
                dokument=dokument,
                uzivatel=user,
            )
            zmena.save()

            messages.add_message(request, messages.SUCCESS, c.OBJECT_UPDATED_SUCCESSFULLY)
            logger.debug("Upraven autor pro dokument " + ident_cely)

        else:
            logger.debug("Form is not valid")
            logger.debug(editAuthorForm.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)

        response = redirect('/documents/create/' + ident_cely)

    else:
        autori = dokument.autor.split(";")
        autori_ids = []
        order = 0
        initial = {}
        # Get id from the authors cache
        for autor in autori:
            a = autor.lstrip()
            try:
                autor_rec = get_object_or_404(HeslarJmena, vypis_cely=a)
                autori_ids.append(autor_rec.id)
            except:
                logger.warning("Nelze najít autora v heslari jmen s vypis_cely=" + a)

        for a in autori_ids:
            order += 1
            initial['author' + str(order)] = a

        editAuthorForm = EditAuthorForm(initial=initial, names=[('', '----')] + names)
        response = render(request, 'documents/author-edit.html', {
            'editAuthorForm': editAuthorForm,
            'addNameForm': addNameForm,
            'ident_cely': ident_cely
        })

    return response


@login_required
def create(request, ident_cely='0', **kwargs):

    context = {}
    other_data = {}
    id_modelu = -1
    sid = request.COOKIES.get('sessionId')
    current_user = kwargs['user']
    user = get_object_or_404(UserStorage, pk=current_user['id'])

    if request.method == 'POST':
        formCreate = CreateForm(request.POST)

        if formCreate.is_valid():
            document_type = formCreate.cleaned_data[c.DOCUMENT_TYPE]
            document_organisation = formCreate.cleaned_data[c.DOC_AUTHORS_ORGANIZATION]
            document_creation_year = formCreate.cleaned_data[c.DOC_YEAR_OF_CREATION]
            document_original_label = formCreate.cleaned_data[c.DOC_ORIGINAL_LABEL]
            document_description = formCreate.cleaned_data[c.DOC_DESCRIPTION]
            document_note = formCreate.cleaned_data[c.DOC_NOTE]

            # Komponenta
            other_data['document_obdobi'] = formCreate.cleaned_data['obdobi']
            other_data['document_areal'] = formCreate.cleaned_data['areal']
            other_data['presna_datace'] = formCreate.cleaned_data['presna_datace']
            other_data['aktivita'] = formCreate.cleaned_data['aktivity']
            other_data['duveryhodnost'] = formCreate.cleaned_data['duveryhodnost']
            # Extra_data
            odkaz = formCreate.cleaned_data[c.DOC_LINK]
            document_plan_format = formCreate.cleaned_data[c.DOC_FORMAT]
            zeme = formCreate.cleaned_data[c.DOC_COUNTRY]
            region = formCreate.cleaned_data[c.DOC_REGION]
            sirka = formCreate.cleaned_data['sirka']
            delka = formCreate.cleaned_data['delka']

            params = {}
            if (document_type):
                params[c.DOCUMENT_TYPE] = str(document_type)
            if (document_organisation):
                params[c.DOC_AUTHORS_ORGANIZATION] = str(document_organisation)
            if (document_creation_year):
                params[c.DOC_YEAR_OF_CREATION] = str(document_creation_year)
            if (document_original_label):
                params[c.DOC_ORIGINAL_LABEL] = str(document_original_label)
            if (document_description):
                params[c.DOC_DESCRIPTION] = str(document_description)
            if (document_note):
                params[c.DOC_NOTE] = str(document_note)
            if (document_plan_format):
                params[c.DOC_FORMAT] = str(document_plan_format)
            if (odkaz):
                params[c.DOC_LINK] = str(odkaz)
            if (zeme):
                params[c.DOC_COUNTRY] = str(zeme)
            if (region):
                params[c.DOC_REGION] = str(region)
            if (sirka):
                params['northing'] = str(sirka)
            if (delka):
                params['easting'] = str(delka)

            resp = []
            # Creating the model
            if(ident_cely == '0'):
                PRIMARY_DIGITAL_ID = 1
                params['autor'] = 'Nezadán'  # Must be not null when creating the model
                params['odpovedny_pracovnik_vlozeni'] = str(current_user['id'])
                params['datum_vlozeni'] = helper.getCurrentEpochTime()
                params['ulozeni_originalu'] = PRIMARY_DIGITAL_ID
                resp = xmlrpc.create_update_3D_model(sid, 'create', params)
                if resp[0]:
                    model = get_object_or_404(Dokument, pk=resp[1])
                    model.stav = c.DRAFT_STATE_ID

                    # Update duveryhodnost in extra_data
                    extra_data = get_object_or_404(ExtraData, dokument=resp[1])
                    extra_data.duveryhodnost = other_data['duveryhodnost']

                    extra_data.save()
                    model.save()
                    # Model should already have its jednotka_dokument and extra_data created by the php server
                    jednotka = model.jednotkadokument_set.all()[0]
                    # Add only one component
                    komponenta = KomponentaDokument(
                        jednotka_dokument=jednotka,
                        ident_cely=model.ident_cely + '-K01',
                        parent_poradi=1
                    )
                    komponenta.save()

                    zmena = HistorieDokumentu(
                        typ_zmeny=c.ZAPSANI,
                        dokument=model,
                        uzivatel=user,
                    )
                    zmena.save()

                    messages.add_message(request, messages.SUCCESS, c.OBJECT_CREATED_SUCCESSFULLY)
                    response = redirect('/documents/create/' + model.ident_cely)
                else:
                    logger.debug("Model could not be created." + str(resp))
                    messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_CREATED)
                    response = redirect('/documents/create/')

            # Updating the model
            else:
                model = get_object_or_404(Dokument, ident_cely=ident_cely)
                # Set updating parameters to the document table
                params['id'] = model.id_id
                # Update of the document, extra_data and jednotka_dokument
                if 'button_save' in request.POST:
                    resp = update(request, params, other_data, model, user, sid)
                elif 'button_send_modal_to_confirm' in request.POST:
                    resp = odeslani(request, params, model, user, sid)
                elif 'button_archive' in request.POST:
                    resp = archivace(request, params, model, user, sid)
                if 'button_delete' in request.POST:
                    resp = model.delete()
                    if resp[0] > 0:
                        logger.debug("Objekt " + str(resp) + ' smazán')
                        messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)
                        return redirect('/documents/create/')
                    else:
                        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_DELETED)

                # Reload model in case ident_cely has been changed
                model = get_object_or_404(Dokument, pk=model.id.id)
                response = redirect('/documents/create/' + model.ident_cely)
            return response

        else:
            logger.debug('Form is not valid')
            logger.debug(formCreate.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)

    if request.method == 'GET':
        if ident_cely == '0':
            # Empty form
            context['showDetails'] = False
            context['canEdit'] = True
            context['canArchive'] = False
            formCreate = CreateForm()
        else:
            # Detail of the 3D model
            context['showDetails'] = True
            model = get_object_or_404(Dokument, ident_cely=ident_cely)
            jednotka = JednotkaDokument.objects.get(dokument=model.id.id)
            komponenta, created = KomponentaDokument.objects.get_or_create(
                jednotka_dokument=jednotka,
                ident_cely=model.ident_cely + '-K01',
                parent_poradi=1)
            if created:
                logger.debug("Vytvorena komponenta(" + str(komponenta.id) +
                             ") dokumentu pro jednotku dokumentu: " + str(jednotka.id))
            context['indet_komponenta'] = komponenta.ident_cely
            id_modelu = model.id_id
            aktivity = []
            areal = 0
            obdobi = 0
            autori = model.autor.split(";")
            if len(autori) == 1 and autori[0] == c.NOT_ENTERED_AUTHOR:
                autori = []

            if komponenta.aktivita_sidlistni:
                aktivity.append(c.AKTIVITA_SIDLISTNI_ID)
            if komponenta.aktivita_pohrebni:
                aktivity.append(c.AKTIVITA_POHREBNI_ID)
            if komponenta.aktivita_vyrobni:
                aktivity.append(c.AKTIVITA_VYROBNI_ID)
            if komponenta.aktivita_tezebni:
                aktivity.append(c.AKTIVITA_TEZEBNI_ID)
            if komponenta.aktivita_kultovni:
                aktivity.append(c.AKTIVITA_KULTOVNI_ID)
            if komponenta.aktivita_komunikace:
                aktivity.append(c.AKTIVITA_KOMUNIKACE_ID)
            if komponenta.aktivita_deponovani:
                aktivity.append(c.AKTIVITA_DEPONOVANI_ID)
            if komponenta.aktivita_boj:
                aktivity.append(c.AKTIVITA_BOJ_ID)
            if komponenta.aktivita_jina:
                aktivity.append(c.AKTIVITA_JINA_ID)
            if komponenta.aktivita_intruze:
                aktivity.append(c.AKTIVITA_INTRUZE_ID)

            if komponenta.obdobi:
                obdobi = komponenta.obdobi.id
            if komponenta.areal:
                areal = komponenta.areal.id

            form_data = {
                'typ_dokumentu': model.typ_dokumentu.id,
                'organizace_autora': model.organizace,
                'rok_vzniku': model.rok_vzniku,
                'oznaceni_originalu': model.oznaceni_originalu,
                'popis': model.popis,
                'poznamka': model.poznamka,
                'format': model.extradata.format,
                'duveryhodnost': model.extradata.duveryhodnost,
                'odkaz': model.extradata.odkaz,
                'region': model.extradata.region,
                'obdobi': obdobi,
                'areal': areal,
                'presna_datace': komponenta.presna_datace,
                'aktivity': aktivity
            }

            geom = model.extradata.geom
            if geom:
                point = wkb.loads(model.extradata.geom, hex=True)
                form_data['sirka'] = point.y
                form_data['delka'] = point.x
            try:
                zeme = model.extradata.zeme
                if zeme:
                    form_data['zeme'] = zeme.id
            except HeslarZeme.DoesNotExist:
                form_data['zeme'] = ''

            # Mapovani pole druh_nalezu na id ze spravneho heslare
            nalezy_list = list(komponenta.nalezdokument_set.values())
            for n in nalezy_list:
                typ_n = n['typ_nalezu_id']
                druh_n = n['druh_nalezu']
                n['typ_nalezu'] = HeslarTypNalezu.objects.get(pk=typ_n).nazev
                if typ_n == PREDMET_OPTION and druh_n:
                    n['druh_nalezu'] = HeslarPredmetDruh.objects.get(pk=druh_n).nazev
                elif typ_n == OBJEKT_OPTION and druh_n:
                    n['druh_nalezu'] = HeslarObjektDruh.objects.get(pk=druh_n).nazev
                else:
                    n['druh_nalezu'] = ''

            # print(data)

            curr_role_opr = helper.get_roles_and_permissions(current_user['auth'])
            soubory = xmlrpc.nacti_vazby(sid, 'dokument_soubor', model.id_id)
            curr_opravneni = curr_role_opr['opravneni']
            stav_int = model.stav
            isDraft = True if (stav_int == c.DRAFT_STATE_ID) and (
                (current_user['id'] == model.odpovedny_pracovnik_vlozeni.id.id) or (c.ADMIN3D in curr_opravneni)) else False
            isArchivinig = True if (stav_int == c.SENT_STATE_ID) and (c.ADMIN3D in curr_opravneni) else False
            #isDearchiving = True if (stav_int == c.ARCHIVED_STATE_ID) and (c.ADMIN3D in curr_opravneni) else False
            context['soubory'] = soubory
            context['stav'] = c.DOCUMENT_STATE_CACHE[stav_int][1]
            context['canArchive'] = isArchivinig
            context['canEdit'] = isDraft or isArchivinig
            context['canSend'] = isDraft
            context['canReturn'] = isArchivinig
            context['autori'] = autori
            context['nalezy'] = nalezy_list

            formCreate = CreateForm(initial=form_data, readonly=not context['canEdit'])
            # print('Moje opravneni: ' + str(curr_opravneni))
            print('Can edit: ' + str(context['canEdit']))
            # print('Can send: ' + str(context['canSend']))
            # print('Can return: ' + str(context['canReturn']))
            # print('Can archive: ' + str(context['canArchive']))

    return render(request, 'documents/create.html', {
        'formCreate': formCreate,
        'documentId': id_modelu,
        'ident_cely': ident_cely,
        'context': context,
    })


@login_required
def choose(request, *args, **kwargs):

    sid = request.COOKIES.get('sessionId')
    context = {}
    names = xmlrpc.get_list(sid, 'jmena', 'prijmeni', 'jmeno')
    users = UserStorage.objects.all().values('id', 'prijmeni', 'jmeno', 'ident_cely')
    usersList = []
    for user in users:
        if user['id'] != -1:
            usersList.append((user['id'], user['prijmeni'] + ", " + user['jmeno'] + " (" + user['ident_cely'] + ")"))

    if request.method == 'POST':
        form = ChooseForm(request.POST, names=names, users=usersList)

        if form.is_valid():

            o = Dokument.objects.filter(rada_id=c.MODELY_DOCUMENTS_ID).select_related('extradata')
            o = filter_documents(o, form.cleaned_data)

            context['table'] = o
            context['doc_states'] = c.DOCUMENT_STATE_DICT
            context['org_dict'] = c.ORGANIZATIONS_CACHE_DICT
            context['active_items'] = [c.MENU_LIBRARY, c.MENU_CHOOSE_3D]

            return render(request, 'documents/list.html', {'context': context})
        else:
            logger.debug('Form is not valid')
            logger.debug(form.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)
    else:
        formChoose = ChooseForm(names=names, users=usersList)

    return render(request, 'documents/choose.html', {
        'formChoose': formChoose,
    })


@login_required
@csrf_protect
def index(request, **kwargs):
    response = render(request, 'documents/index.html')
    return response


def logout(request, **kwargs):
    response = redirect('login')
    response.delete_cookie('sessionId')
    response.delete_cookie('django_language')
    return response


# Validation here for login (if user doesen't exist)
@csrf_protect
def login(request, **kwargs):

    if request.method == 'GET':
        sid = request.COOKIES.get('sessionId')

        formLogin = LoginForm()

        if(sid is None):
            sid = xmlrpc.get_sid()
            response = render(request, 'documents/login.html', {'formLogin': formLogin})
            helper.set_cookie(response, 'sessionId', sid)
        else:
            try:
                user = xmlrpc.get_current_user(sid)
                if (user):
                    if 'next' in request.GET:
                        response = redirect(request.GET.get('next'))
                    else:
                        response = redirect('home')
                else:
                    response = render(request, 'documents/login.html', {'formLogin': formLogin})
            except:
                # Should only catch 500 from xmlrpc
                logger.debug("Sid of the user probably expired. Loggin out.")
                response = redirect('logout')
                response.delete_cookie('sessionId')
                response.delete_cookie('django_language')

    if (request.method == 'POST'):

        formLogin = LoginForm(request.POST)

        if(formLogin.is_valid()):

            #  Get sid
            sid = xmlrpc.get_sid()
            # Login on the server side
            susername = formLogin.cleaned_data['login_username']
            spassword = formLogin.cleaned_data['login_password']

            try:
                loginResp = xmlrpc.login(sid, susername, spassword)
            except:
                logger.error("Could not log in with sid " + sid + " logging out ...")
                # If exception is thrown try to redirect to logout to get a new sid
                response = redirect('logout')
                return response

            if (loginResp == 1):
                # Cache store
                timestamp = int(datetime.timestamp(datetime.now()))

                # Check if there was not next in the post request
                if 'next' in request.POST:
                    response = redirect(request.POST.get('next'))
                else:
                    response = redirect('home')

                helper.set_cookie(response, 'lstamp', timestamp, max_age_seconds=36000)
                helper.set_cookie(response, 'sessionId', sid)

                # Check preferred language and store it into cookie
                user = get_object_or_404(UserStorage, email__iexact=susername)
                helper.set_cookie(response, 'django_language', user.jazyk)

            elif (loginResp == -3):
                formLogin.add_error(None, "Nesprávné přihlašovací jméno nebo heslo.")
                response = render(request, 'documents/login.html', {'formLogin': formLogin})
            elif (loginResp == -4):
                formLogin.add_error(
                    None, "Nemáte level autorizace nebo je Váš účet neaktivní. Obraďte se na administrátora.")
                response = render(request, 'documents/login.html', {'formLogin': formLogin})
            elif (loginResp == -5):
                formLogin.add_error(None, "Omlouváme se, je plánovaná odstávka servru. Zkuste to prosím později.")
                response = render(request, 'documents/login.html', {'formLogin': formLogin})
            else:
                print("Could not log in. Resp: " + str(loginResp))
            # If Login is sucessfull redirect to index.html
            # if Login is not sucessfull render ???????
        else:
            print("Form is invalid")
            response = render(request, 'documents/login.html', {'formLogin': formLogin})

    return response


@login_required
def my_models(request, **kwargs):

    context = {}
    current_user = kwargs['user']
    o = Dokument.objects.select_related('extradata').filter(
        rada_id=c.MODELY_DOCUMENTS_ID).filter(
        odpovedny_pracovnik_vlozeni=current_user['id']
    )

    context['table'] = o
    context['doc_states'] = c.DOCUMENT_STATE_DICT
    context['org_dict'] = c.ORGANIZATIONS_CACHE_DICT
    context['active_items'] = [c.MENU_LIBRARY, c.MENU_LIST_3D]

    return render(request, 'documents/list.html', {'context': context})


@login_required
def manage_models(request, **kwargs):

    context = {}
    current_user = kwargs['user']
    role_opravneni = helper.get_roles_and_permissions(int(current_user['auth']))
    if c.ADMIN3D in role_opravneni['opravneni']:
        o = Dokument.objects.select_related('extradata').filter(
            rada_id=c.MODELY_DOCUMENTS_ID).filter(
            stav=c.SENT_STATE_ID)
        context['table'] = o

    context['doc_states'] = c.DOCUMENT_STATE_DICT
    context['org_dict'] = c.ORGANIZATIONS_CACHE_DICT
    context['active_items'] = [c.MENU_LIBRARY, c.MENU_MANAGE_3D]

    return render(request, 'documents/list.html', {'context': context})


@min_user_group(c.ARCHEOLOG)
def return_model(request, ident_cely, **kwargs):
    logger.debug("Vraceni nalezu: " + ident_cely)

    current_user = kwargs['user']
    model = get_object_or_404(Dokument, ident_cely=ident_cely)
    stavy = dict(c.DOCUMENT_STATE_CACHE)
    user_id = str(current_user['id'])
    user = get_object_or_404(UserStorage, pk=user_id)
    stary_stav_id = model.stav

    if (stary_stav_id != c.SENT_STATE_ID) and (stary_stav_id != c.ARCHIVED_STATE_ID):
        logger.debug("Nepovoleny stav vraceni: " + str(stary_stav_id) + " Povolene stavy: " +
                     str(c.SENT_STATE_ID) + ", " + str(c.ARCHIVED_STATE_ID))
        return render(request, '403.html')

    stary_stav = stavy[model.stav]
    novy_stav = stavy[model.stav - 1]

    if request.method == 'POST':
        form = ReturnFindingForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data['reason']
            logger.debug("Return reason is: " + reason)

            if stary_stav_id == c.ARCHIVED_STATE_ID:
                vraceni_modelu(request, user, model, reason, c.SENT_STATE_ID, c.ZPET_K_ODESLANI)

            if stary_stav_id == c.SENT_STATE_ID:
                vraceni_modelu(request, user, model, reason, c.DRAFT_STATE_ID, c.ZPET_K_ZAPSANI)

            response = redirect('/documents/create/' + model.ident_cely)

        else:
            logger.debug("Form is not valid")
            logger.debug(form.errors)
            messages.add_message(request, messages.WARNING, c.FORM_IS_NOT_VALID)
            response = render(request, 'documents/vrat_dokument.html', {'form': form})

    else:
        form = ReturnFindingForm()

        response = render(request, 'documents/vrat_dokument.html', {
            'form': form,
            'model': model,
            'old_state': stary_stav,
            'new_state': novy_stav
        })

    return response


def model_history(request, ident_cely):

    model = Dokument.objects.get(ident_cely=ident_cely)

    historie = HistorieDokumentu.objects.filter(dokument=model)

    return render(request, 'documents/history_models.html', {
        'historie': historie,
        'ident_cely': ident_cely
    })


####################################### NON-VIEW FUNCTIONS #######################################

def odeslani(request, params, model, user, sid):
    logger.debug("Odeslani modelu : " + str(model.id))

    model.stav = c.SENT_STATE_ID
    model.save()

    zmena = HistorieDokumentu(
        typ_zmeny=c.ODESLANI,
        dokument=model,
        uzivatel=user,
    )
    zmena.save()

    messages.add_message(request, messages.SUCCESS, c.OBJECT_SENT_SUCCESSFULLY)


def archivace(request, params, model, user, sid):
    logger.debug("Archivace modelu : " + str(model.id.id))

    params['odpovedny_pracovnik_archivace'] = user.id.id
    params['datum_archivace'] = helper.getCurrentEpochTime()
    params['archivovat_dokument'] = True
    resp = xmlrpc.create_update_3D_model(sid, 'update', params)

    if resp[0]:
        zmena = HistorieDokumentu(
            typ_zmeny=c.ARCHIVACE,
            dokument=model,
            uzivatel=user,
        )
        zmena.save()
        messages.add_message(request, messages.SUCCESS, c.OBJECT_ARCHIVED_SUCCESSFULLY)
    else:
        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_UPDATED)


def vraceni_modelu(request, user, model, reason, state_id, transition_id):
    logger.debug("Vraceni modelu : " + str(model.id.id))

    model.stav = state_id
    model.save(update_fields=["stav"])

    zmena = HistorieDokumentu(
        typ_zmeny=transition_id,
        dokument=model,
        uzivatel=user,
        duvod=reason
    )
    zmena.save()
    messages.add_message(request, messages.SUCCESS, c.OBJECT_RETURNED_TO_PREVIOUS_STATE)


def update(request, params, other_data, model, user, sid):
    logger.debug("Aktualizace modelu : " + model.ident_cely)

    resp = xmlrpc.create_update_3D_model(sid, 'update', params)
    if resp[0]:

        jednotka = model.jednotkadokument_set.all()[0]
        komponenta = jednotka.komponentadokument_set.all()[0]
        extra_data = model.extradata
        # Update komponenta_dokument
        if other_data['document_obdobi']:
            obdobi = HeslarObdobiDruha.objects.get(pk=other_data['document_obdobi'])
            komponenta.obdobi = obdobi
        else:
            komponenta.obdobi = None
        if other_data['document_areal']:
            areal = HeslarArealDruha.objects.get(pk=other_data['document_areal'])
            komponenta.areal = areal
        else:
            komponenta.areal = None
        if other_data['presna_datace']:
            komponenta.presna_datace = other_data['presna_datace']
        else:
            komponenta.presna_datace = None
        if other_data['duveryhodnost']:
            extra_data.duveryhodnost = other_data['duveryhodnost']
        else:
            model.extradata.duveryhodnost = None
        for a in other_data['aktivita']:
            if a == str(c.AKTIVITA_SIDLISTNI_ID):
                komponenta.aktivita_sidlistni = True
            if a == str(c.AKTIVITA_POHREBNI_ID):
                komponenta.aktivita_pohrebni = True
            if a == str(c.AKTIVITA_VYROBNI_ID):
                komponenta.aktivita_vyrobni = True
            if a == str(c.AKTIVITA_TEZEBNI_ID):
                komponenta.aktivita_tezebni = True
            if a == str(c.AKTIVITA_KULTOVNI_ID):
                komponenta.aktivita_kultovni = True
            if a == str(c.AKTIVITA_KOMUNIKACE_ID):
                komponenta.aktivita_komunikace = True
            if a == str(c.AKTIVITA_DEPONOVANI_ID):
                komponenta.aktivita_deponovani = True
            if a == str(c.AKTIVITA_BOJ_ID):
                komponenta.aktivita_boj = True
            if a == str(c.AKTIVITA_JINA_ID):
                komponenta.aktivita_jina = True
            if a == str(c.AKTIVITA_INTRUZE_ID):
                komponenta.aktivita_intruze = True
        komponenta.save()
        extra_data.save()

        zmena = HistorieDokumentu(
            typ_zmeny=c.AKTUALIZACE,
            dokument=model,
            uzivatel=user,
        )
        zmena.save()

        messages.add_message(request, messages.SUCCESS, c.OBJECT_UPDATED_SUCCESSFULLY)
    else:
        messages.add_message(request, messages.WARNING, c.OBEJCT_COULD_NOT_BE_UPDATED)

    return resp


# Returns filterd documents which have related KomponentaDokument from the list
def filter_related_document_komponent(o, komponenty):
    queries = []
    for k in komponenty:
        queries.append(Q(pk=k.jednotka_dokument.dokument.id.id))
    query = queries.pop()
    for item in queries:
        query |= item
    return o.filter(query)


def filter_documents(o, options):

    if options['ident_cely']:
        logger.debug("Filtruji podle ident_cely ...")
        o = o.filter(ident_cely__icontains=options['ident_cely'])
    if options['rok_vzniku']:
        logger.debug("Filtering rok_vzniku ...")
        o = o.filter(rok_vzniku=options['rok_vzniku'])
    if options['organizace']:
        logger.debug("Filtering organizace ...")
        o = o.filter(organizace=options['organizace'])
    if options['typ_dokumentu']:
        logger.debug("Filtering typ_dokumentu ...")
        o = o.filter(typ_dokumentu__id=options['typ_dokumentu'])
    if options['popis']:
        logger.debug("Filtering popis ...")
        o = o.filter(popis__icontains=options['popis'])
    if options['duveryhodnost'] != '0':
        logger.debug("Filtering duveryhodnost ...")
        o = o.filter(extradata__duveryhodnost__gte=options['duveryhodnost'])
    if options['procesni_stavy']:
        logger.debug("Filtering procesni_stavy ...")
        queries = [Q(stav=value) for value in options['procesni_stavy']]
        query = queries.pop()
        for item in queries:
            query |= item
        o = o.filter(query)
    for autor_id in options['autori']:
        logger.debug("Filtering authors ...")
        a = get_object_or_404(HeslarJmena, pk=autor_id)
        o = o.filter(autor__contains=a.vypis_cely)
    if options['obdobi']:
        logger.debug("Filtering obdobi ...")
        queries = [Q(obdobi_id=value) for value in options['obdobi']]
        query = queries.pop()
        for item in queries:
            query |= item
        komponenty = KomponentaDokument.objects.filter(query)
        if komponenty:
            o = filter_related_document_komponent(o, komponenty)
    if options['areal']:
        logger.debug("Filtering areal ...")
        komponenty = KomponentaDokument.objects.filter(areal_id=options['areal'])
        if komponenty:
            o = filter_related_document_komponent(o, komponenty)
    if options['aktivity']:
        logger.debug("Filtering aktivity...")
        fields = {}
        for i in options['aktivity']:
            fields['jednotkadokument__komponentadokument__' + c.AKTIVITY_FIELDS[int(i)]] = True
        queries = []
        for key, val in fields.items():
            queries.append(Q(**{key: val}))
        query = queries.pop()
        for item in queries:
            query |= item
        o = o.distinct().filter(query)

    # Dle nalezu
    if options['druh_objektu']:
        logger.debug("Filtruji podle druhu objektu...")
        o = o.distinct().filter(
            jednotkadokument__komponentadokument__nalezdokument__druh_nalezu=options['druh_objektu']).filter(
            jednotkadokument__komponentadokument__nalezdokument__typ_nalezu=1
        )
    if options['druh_predmetu']:
        logger.debug("Filtruji podle druhu predmetu...")
        o = o.distinct().filter(
            jednotkadokument__komponentadokument__nalezdokument__druh_nalezu=options['druh_predmetu']).filter(
            jednotkadokument__komponentadokument__nalezdokument__typ_nalezu=2
        )
    if options['specifikace_objektu']:
        logger.debug("Filtruji podle specifikace_objektu...")
        o = o.distinct().filter(
            jednotkadokument__komponentadokument__nalezdokument__specifikace=options['specifikace_objektu']).filter(
            jednotkadokument__komponentadokument__nalezdokument__typ_nalezu=1
        )
    if options['specifikace_predmetu']:
        logger.debug("Filtruji podle specifikace_predmetu...")
        o = o.distinct().filter(
            jednotkadokument__komponentadokument__nalezdokument__specifikace=options['specifikace_predmetu']).filter(
            jednotkadokument__komponentadokument__nalezdokument__typ_nalezu=2
        )

    if options['zmeny']:
        logger.debug("Filtruji podle typu zmeny...")
        o = o.distinct().filter(historiedokumentu__typ_zmeny=options['zmeny'])
    if options['zmena_od']:
        from_date = datetime.strptime(options['zmena_od'], "%d/%m/%Y")
        if options['zmeny']:
            logger.debug("Filtruji zmeny od data a typu zmeny...")
            o = o.distinct().filter(historiedokumentu__datum_zmeny__gte=from_date, historiedokumentu__typ_zmeny=options['zmeny'])
        else:
            logger.debug("Filtruji zmeny od data...")
            o = o.distinct().filter(historiedokumentu__datum_zmeny__gte=from_date)
    if options['zmena_do']:
        to_date = datetime.strptime(options['zmena_do'], "%d/%m/%Y")
        if options['zmeny']:
            logger.debug("Filtruji zmeny do data a typu zmeny...")
            o = o.distinct().filter(historiedokumentu__datum_zmeny__lte=to_date, historiedokumentu__typ_zmeny=options['zmeny'])
        else:
            logger.debug("Filtruji zmeny do data...")
            o = o.distinct().filter(historiedokumentu__datum_zmeny__lte=to_date)
    if options['zmena_uzivatel']:
        logger.debug("Filtruji podle uzivatele zmeny ...")
        o = o.distinct().filter(historiedokumentu__uzivatel=options['zmena_uzivatel'])

    return o
