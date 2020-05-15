import logging
import socket

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from documents.constants import AmcrConstants as c
from documents import helper, xmlrpc
from . import models


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
                for one_project in projects:
                    project_organizace = models.UserStorage.objects.get(id=one_project[2]).organizace.id

                    for one_link in my_links:
                        #print("compare: "+str(one_link[2])+" "+str(project_organizace))
                        if one_link[2] == project_organizace:
                            #print("Pripojuji si tento projekt: "+str(one_project))
                            my_projects.append((one_project[0], one_project[1]))
                return my_projects
            elif curr_role == c.ARCHEOLOG:  # Archeolog can see all projects his organization
                for one_project in projects:
                    project_organizace = models.UserStorage.objects.get(id=one_project[2]).organizace.id
                    organizace_archeolog = models.UserStorage.objects.get(id=badatel_id).organizace.id
                    if project_organizace == organizace_archeolog:
                        my_projects.append((one_project[0], one_project[1]))
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
