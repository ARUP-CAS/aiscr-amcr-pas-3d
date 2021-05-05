import logging
import socket

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from documents.constants import AmcrConstants as c
from detectors.constants import DetectorConstants as dc
from documents import helper, xmlrpc
from . import models
from detectors.models import Projekt
from django.db.models.functions import Concat
from django.db.models import CharField, Value


logger = logging.getLogger(__name__)


def detector(request, params):
    try:
        sid = request.COOKIES.get('sessionId')
        detector_ids = xmlrpc.hledej_detektor(sid, params)
        ids = []
        for i in range(len(detector_ids)):
            ids.append(detector_ids[i]['id'])
        # Get details of the documents
        detail = xmlrpc.nacti_informace_list(sid, 'detektor', ids)
    except socket.gaierror as ex:
        message = 'Connection error. Is amcr server reachable?'
        explanation = 'Nodename nor servname provided, or not known'
        logger.error(message)
        return JsonResponse({'message': message, 'explanation': explanation}, status=500)

    return detail


def load_my_active_links(badatel_id):
    my_links = []
    all_links = []
    all_links = models.VazbaSpoluprace.objects.filter(badatel=badatel_id, aktivni=True, potvrzeno=True)
    for one_link in all_links:
        #print("-----one link: "+str(one_link.archeolog.id.id))
        organizace_archeolog = models.UserStorage.objects.get(id=one_link.archeolog.id).organizace.id
        my_links.append((badatel_id, one_link.archeolog.id.id, organizace_archeolog))
        #print("Pripojuji si vazbu: " + str(badatel_id) +" " + str(one_link.archeolog.id.id) + " " + str(organizace_archeolog))
    return my_links


def load_my_projects(badatel_id, projects):
    my_projects = []
    my_links = []
    curr_auth = get_object_or_404(models.UserGroupAuthStorage, Q(
        id__item_type=-10) & Q(user_group=badatel_id)).auth_level
    curr_role = helper.get_roles_and_permissions(curr_auth)['role']
    if curr_role in (c.ARCHIVAR, c.ADMIN):
        return projects  # Archivar and Admin can see all projects
    else:
        try:
            if curr_role == c.BADATEL:  # Badatel can see projects if he has active coorporation with archeolog, organization of this archeolog created this project
                my_links = load_my_active_links(badatel_id)
                # Removing duplicate links (when two cooperations are with archeologists from the same organization)
                my_organizations = set()
                for link in my_links:
                    my_organizations.add(link[2])
                for one_project in projects:
                    project_organizace = models.UserStorage.objects.get(id=one_project['odpovedny_pracovnik_prihlaseni']).organizace.id
                    for organization in my_organizations:
                        if organization == project_organizace:
                            my_projects.append(one_project)
                return my_projects
            elif curr_role == c.ARCHEOLOG:  # Archeolog can see all projects his organization
                for one_project in projects:
                    project_organizace = models.UserStorage.objects.get(id=one_project['odpovedny_pracovnik_prihlaseni']).organizace.id
                    organizace_archeolog = models.UserStorage.objects.get(id=badatel_id).organizace.id
                    if project_organizace == organizace_archeolog:
                        my_projects.append(one_project)
                return my_projects
            else:
                return my_projects

        except:
            #print("----chyba load_my_projects")
            # print(sys.exc_info())
            return my_projects


def get_id_name_by_user_id(user_id):
    # Par postrehu
    # 1. Jmeno a prijemeni v tabulce user_storage nemusi byt unikatni (v tabulce jmen musi, co znamena ze dva lidi se stejnou kombinaci jmena a prijmeni budou ukazovat na stejny zaznam v heslari jmen)
    # 2. V pripade ze si uzivatel zmeni prijmeni (napr. po svadbe) a to se
    # neaktualizuje v heslari jmen, zaznam nebude nalezen
    try:
        user = models.UserStorage.objects.get(id=user_id)
        vypis_cely = user.prijmeni + ', ' + user.jmeno
        name = models.HeslarJmena.objects.get(vypis_cely=vypis_cely)
        return name.id
    except:
        logger.error("Could not map user with id " + str(user_id) + " to name record.")
        return -1

def get_vypis_cely_by_id_name(name_id):
    name = ''
    try:
        name = models.HeslarJmena.objects.get(id=name_id).vypis_cely
    except:
        logger.error("Could not find name")

    return name

def projekty_vyzkumne():
    RESEARCH_PROJECT_ID = 3
    projekty = Projekt.objects.filter(typ_projektu=RESEARCH_PROJECT_ID).values('id', 'ident_cely', 'odpovedny_pracovnik_prihlaseni', 'vedouci_projektu')
    return projekty

def projekty_zahajene_ukoncene_v_terenu(projekty):
    return projekty.filter(Q(stav=dc.PROJEKT_STAV_UKONCENY) | Q(stav=dc.PROJEKT_STAV_ZAHAJENY)).order_by("-ident_cely")

def prijmeni_jmeno():
    qs = models.HeslarJmena.objects.annotate(prijmeni_jmeno=Concat('prijmeni', Value(', '), 'jmeno')).all()
    return qs.values_list('id', 'prijmeni_jmeno')
