import xmlrpc.client
import logging
import hashlib
import os
import re
#import inspect

from .constants import AmcrConstants as constants
from . import helper
from . import ftp

from django.conf import settings
from xml.parsers.expat import ExpatError

logger = logging.getLogger(__name__)

MOCK_SERVER_ADDR = "http://localhost:8888/"
DEV_SERVER_ADDR = 'https://' + settings.AMCR_API + "/xmlrpc/0/?t=600"
SERVER_ADDR = ''

# ------- Requests on the development server --------
def get_sid():
    logger.debug("xmlrpc.get_sid called")
    server = getServerAddr()
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        resp = str(proxy.get_sid())
        return resp


def get_list(sessionId, inventoryName, columnName='caption', descriptionColumnName=None, poradi=False):
    logger.debug("xmlrpc.get_list called %s", inventoryName)
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_list(sessionId, inventoryName)
        # print(resp)
        inventoryList = []
        for i in range(2, len(resp)):
            if not poradi:
                if(descriptionColumnName is None):
                    k = (resp[i]['id'], resp[i][columnName])
                    inventoryList.append(k)
                else:
                    k = (resp[i]['id'], resp[i][columnName] + ', ' + resp[i][descriptionColumnName])
                    inventoryList.append(k)
            else:
                if(descriptionColumnName is None):
                    k = (resp[i]['id'], resp[i][columnName], int(resp[i]['poradi']))
                    inventoryList.append(k)
                else:
                    k = (resp[i]['id'], resp[i][columnName] + ', ' + resp[i]
                         [descriptionColumnName], int(resp[i]['poradi']))
                    inventoryList.append(k)
        if poradi:
            # Sort according to poradi
            inventoryList.sort(key=lambda tup: tup[2])
            # Remove poradi from the list
            inventoryList = [(i[0], i[1]) for i in inventoryList]
        return inventoryList


def get_dict(sessionId, inventoryName):
    logger.debug("xmlrpc.get_dict called %s", inventoryName)
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_list(sessionId, inventoryName)
        return resp[2:]


def get_list_columns(sessionId, inventoryName, columnArray):
    logger.debug("xmlrpc.get_list called %s", inventoryName)
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_list(sessionId, inventoryName)
        # print(resp)
        inventoryList = []
        for i in range(2, len(resp)):
            k = [resp[i]['id']]
            for column in columnArray:
                k.append(resp[i][column])
            inventoryList.append(tuple(k))
        return inventoryList


def hledej_dokument(sessionId, params):
    logger.debug("xmlrpc.hledej dokument called %s", str(params))

    allParams = {
        'aktivita': '-1',
        'areal_druha': '',
        'typ': '-1',
        'okres': '-1',
        'typ_nalezu': '-1',
        'rok_vzniku': '-1',
        'lokalizace_nazev_lokality_mod': '',
        'popis_udalosti': '',
        'pristupnost': '-1',
        'limit': '100',
        'typ_dokumentu': '-1',
        'organizace': '-1',
        'dokumenty_typ': '',
        'db_id_dokumentu': '-1',
        'obdobi_od': '-1',
        'typ_udalosti': '-1',
        'stranka': '0',
        'specifikace_predmet': '-1',
        'autor': '-1',
        'rok_od': '',
        'rok_do': '',
        'dokumenty_id': '',
        'dokumenty_rada': '',
        'dokumenty_autor_mod': '',
        'nalez_predmet_druha': '-1',
        'dokumenty_popis_mod': '',
        'dokumenty_rok_vzniku': '',
        'lokalizace_nazev_lokality': '',
        'zachovalost': '-1',
        'obdobi_nadrazene': '-1',
        'specifikace_zahrnute': '-1',
        'obdobi_zahrnute': '-1',
        'areal_zahrnute': '',
        'uzivatel': '-1',
        'rada': '-1',
        'nalez_objekt_druha': '-1',
        'katastr': '-1',
        'order_ascending': 'asc',
        'specifikace_objekt': '-1',
        'kraj': '-1',
        'dokumenty_organizace': '',
        'areal_prvni': '',
        'popis': '',
        'dokumenty_popis': '',
        'obdobi_do': '-1',
        'dokumenty_autor': '',
        'order_by': 'typ_dokumentu',
        'nalez_zahrnute': '-1',
        'id_cj': '',
        'stav': '-1',
    }

    for k, v in params.items():
        allParams[k] = v

    server = getServerAddr()
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.hledej_dokument(sessionId, helper.create_parameters(allParams))
        # print(str(resp))
        return resp[2:]


def hledej_detektor(sessionId, params):
    logger.debug("xmlrpc.hledej detektor called %s", str(params))

    allParams = {
        'inv_cislo': '-1',
        'projekt': '',
        'katastr': '',
        'lokalizace': '',
        'okolnosti': '',
        'geom': '',
        'pristupnost': '',
        'obdobi': '',
        'presna_datace': '',
        'typ_nalezu': '',
        'druh_nalezu': '',
        'specifikace': '',
        'pocet': '',
        'limit': '10000', # Je potreba mit jinak server nastavi limit na 50
        #'stranka': '0',
        'poznamka': '',
        'nalezce': '-1',
        'datum_nalezu': '',
        #'odpovedny_pracovnik_vlozeni': '-1',
        'datum_vlozeni': '-1',
        'odpovedny_pracovnik_archivace': '-1',
        'datum_archivace': '-1',
        'stav': '',
        'predano': '',
        'predano_organizace': '',
        'poradi': '-1',
        'ident_cely': '-1'
    }

    for k, v in params.items():
        allParams[k] = v
    logger.debug(allParams)
    server = getServerAddr()
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.hledej_detektor(sessionId, helper.create_parameters(allParams))
        # print(str(resp))
        return resp[2:]


def nacti_informace_list(sessionId, tableName, listOfIds):
    logger.debug("xmlrpc.nacti_informace_list called")
    server = getServerAddr()
    detalis = False
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.nacti_informace_list(sessionId, tableName, detalis, listOfIds, False)
        return resp[1:]


def aktualni_cas(sessionId):
    logger.debug("xmlrpc.aktualni_cas called")
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.aktualni_cas(sessionId)
        return resp


def nacti_informace(sessionId, tableName, info_id):
    logger.debug("xmlrpc.nacti_informace called: %s, %s", tableName, str(info_id))
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.nacti_informace(sessionId, tableName, True, str(info_id))
        return resp[1:]


def login(sessionId, username, password):
    logger.debug("xmlrpc.login called")
    server = getServerAddr()
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        stats = '{"timestamp":""}'
        try:
            resp = proxy.login(sessionId, username, hashlib.sha1(password.encode(
                'utf8')).hexdigest(), 'client', settings.LOGIN_KEEP_ALIVE, stats)
        except ExpatError as ex:
            logger.exception("Nelze parsovat odpoved z php servru.")
            raise ex

        return resp


def get_current_user(sessionId):
    #curframe = inspect.currentframe()
    #calframe = inspect.getouterframes(curframe, 2)
    #print('caller name:', calframe[1][3])
    logger.debug("xmlrpc.get_current_user called")
    server = getServerAddr()
    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False, allow_none=True) as proxy:
        resp = proxy.get_current_user(sessionId)
        return resp

# Retrieving users - could be more effective


def get_list_users(sessionId):
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False, allow_none=True) as proxy:
        resp = proxy.get_list(sessionId, constants.USERS)
        return resp


def zmena(sessionId, tableName, methodName, content):
    logger.debug("xmlrpc.zmena called: %s, %s, %s", tableName, methodName, str(content).encode('utf-8'))
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.zmena(sessionId, tableName, methodName, content)
        logger.debug('response:' + str(str(resp[1]).encode('utf-8')))
        return resp


def get_sumarizace(sessionId):
    logger.debug("xmlrpc.get_sumarizace called")
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_sumarizace(sessionId)
        logger.debug('response:' + str(resp))
        return resp


def nacti_vazby(sessionId, relationName, id_vazba):
    logger.debug("xmlrpc.nacti_vazby called %s, %s", relationName, str(id_vazba))
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.nacti_vazby(sessionId, relationName, id_vazba)
        return resp[1:]


def hledej_akce_dokumentu(sessionId, documentId, params):

    allParams = {
        'rozsah': '',
        'typ_akce_vedlejsi': '-1',
        'uzivatelske_oznaceni': '',
        'typ': 'R',
        'okres': '-1',
        'datum_zmeny_do': '',
        'nz_odlozene': '',
        'stav_akce': '-1',
        'pristupnost': '-1',
        'zahrnute': '',
        'limit': '0',
        'jako_projekt': '1',
        'datum_do': '',
        'organizace': '-1',
        'zahajene': '',
        'typ_akce': '-1',
        'obdobi_od': '-1',
        'nz_vracene': '',
        'stranka': '0',
        'vedouci_akce_ostatni': '',
        'odpovedny_pracovnik_zapisu': '-1',
        'datum_zmeny_od': '',
        'rozepsane_sledovani': '',
        'popisne_udaje': '',
        'typ_akce_hlavni': '-1',
        'rozepsane': '',
        'archivovane_zaa': '',
        'dalsi_katastry': '',
        'samostatne_bez_nz_navrzene_k_archivaci': '',
        'nz_podane': '',
        'uzivatel': '-1',
        'zahajene_sledovani': '',
        'k_archivaci': '-1',
        'katastr': '-1',
        'order_ascending': 'asc',
        'samostatne_bez_nz_navrzene_k_archivaci_sledovani': '',
        'stav': '',
        'datum_od': '',
        'kraj': '-1',
        'nadrazene': '',
        'vracene_zaa_sledovani': '',
        'organizace_ostatni': '',
        'obdobi_do': '-1',
        'napojene_na_dokument_id': str(documentId),
        'nz_archivovane': '',
        'nz_odlozene_sledovani': '',
        'archivovane_zaa_sledovani': '',
        'nz_podane_sledovani': '',
        'order_by': 'katastr',
        'nz_archivovane_sledovani': '',
        'nz_vracene_sledovani': '',
        'vedouci_projektu': '-1',
        'id_cj': '',
        'vracene_zaa': '',
    }

    for k, v in params.items():
        allParams[k] = v

    logger.debug("xmlrpc.hledej_akce_dokumentu called %s", str(allParams))

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.hledej_akce(sessionId, helper.create_parameters(allParams))
        return resp[2:]


def hledej_lokality_dokumentu(sessionId, documentId, params):

    document_id = str(documentId)

    allParams = 'aktivita=-1&areal_druha=-1&typ_akce_vedlejsi=-1&uzivatelske_oznaceni=&obdobi_nadrazene=&typ=&okres=-1&presnost_pian=-1&obdobi_zahrnute=&druh=-1&dalsi_katastry=&pristupnost=-1&areal_zahrnute=&uzivatel=-1&limit=0&jako_projekt=1&datum_do=&organizace=-1&katastr=-1&order_ascending=asc&stav=&obdobi_od=-1&datum_od=&kraj=-1&detektory=false&areal_prvni=-1&stranka=0&cj_pian=&odpovedny_pracovnik_zapisu=-1&obdobi_do=-1&napojene_na_dokument_id=' + \
        document_id + '&typ_pian=-1&pian_zm50=-1&popisne_udaje=&order_by=nazev&pian_zm10=-1&typ_akce_hlavni=-1&id_cj=&'

    logger.debug("xmlrpc.hledej_lokality_dokumentu called %s", str(allParams))

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.hledej_lokality(sessionId, allParams)
        return resp[2:]

########################### LESS GENERAL REQUESTS ##########################


def get_model_detail_tree(sessionId, modelId):

    if(modelId == 0) or (modelId is None):
        return {}

    # Find out if model has action or locality
    resp = hledej_akce_dokumentu(sessionId, modelId, {})

    resp_info = nacti_informace(sessionId, 'dokument', modelId)

    komponenty = []
    akce = []
    zaznamy_level_1 = []
    try:
        komponenty = list(resp_info[0]['jds']['0']['komponenta'].values())
        akce = list(resp_info[0]['akce_objects'].values())
        if(len(akce) != 0):
            zaznam = {
                'text': akce[0]['id_cj'],
                'data': akce[0],
                'type': 'event'
            }
            zaznamy_level_1.append(zaznam)

        for v in komponenty:
            zaznam = {
                'text': v['ident_cely'],
                'data': v,
                'type': 'component'
            }
            zaznamy_level_1.append(zaznam)
    except KeyError:
        print('No akce_objects or soubory found in the document info response')

    return zaznamy_level_1


def get_autor_id(sessionId, name, surname):
    logger.debug("xmlrpc.get_list called, jmena")
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_list(sessionId, 'jmena')
        author_id = -1
        for i in range(2, len(resp)):
            if((resp[i]['jmeno'] == name) and (resp[i]['prijmeni'] == surname)):
                author_id = resp[i]['id']
        return author_id

# Give me only document types and formats for 3D models, not all of the records in the glossary


def get_list_3D_model_type_form(sessionId, inventoryName):
    logger.debug("xmlrpc.get_list called, %s", inventoryName)
    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.get_list(sessionId, inventoryName)
        inventoryList = []
        for i in range(2, len(resp)):
            if(resp[i]['model']):
                k = (resp[i]['id'], resp[i]['caption'])
                inventoryList.append(k)
        return inventoryList


def create_update_3D_model(sessionId, keyword, params):

    allParams = {
        # KONSTANTY
        'material_dokument': '1',  # digitalni soubor
        'rada': '16',  # 3D model
        'jazyk_dokumentu': '7',  # N/A Proč 7?
        'letter_cj': '1',  # C
        'pristupnost_dokument': '1',
        # POVINNE
        'typ_dokumentu': '',
        'organizace_autora': '',
        'format': '',
        'rok_vzniku': '',
        #'duveryhodnost': '', Being updated in webamcr
        'oznaceni_originalu': '',
        # DODATECNE INFO
        'popis': '',
        'poznamka': '',
        'odkaz': '',
        # LOKALIZACE OBSAHU
        'pas': '',
        'northing': '',
        'easting': '',
        'zeme': '',
        'region': '',
        # HISTORIE DOKUMENTU
        #'datum_archivace':'', # CANNOT BE -1 for create
        # OSTATNI
        'typ_dokumentu_posudek': '',
        '_index': '',
        #'temp_id':'-1',
        'datum_vzniku': '',
        'zachovalost': '-1',
        'rok_do': '',
        'vyska': '',
        #'ulozeni_originalu':'',
        #'datum_zverejneni':'',
        'udalost_typ': '-1',
        'nahrada': '-1',
        'osoby': '',
        'rok_od': '',
        'meritko': '',
        'udalost': '',
        'sirka': '',
        #'odpovedny_pracovnik_archivace':'',
        'pocet_variant_originalu': '',
        'cislo_objektu': '',
    }

    for k, v in params.items():
        allParams[k] = v

    return zmena(sessionId, 'dokument', keyword, allParams)


###########################################################################
def create_update_detektor(sessionId, keyword, params):

    allParams = {
        'inv_cislo': '-1',
        'projekt': '',
        'katastr': '',
        'lokalizace': '',
        'okolnosti': '',
        'geom': '',
        'pristupnost': '1',
        'obdobi': '',
        'presna_datace': '',
        'typ_nalezu': '2',
        'druh_nalezu': '',
        'specifikace': '',
        'pocet': '',
        'poznamka': '',
        'nalezce': '',
        'datum_nalezu': '',
        'datum_vlozeni': '-1',
        'odpovedny_pracovnik_archivace': '-1',
        'datum_archivace': '-1',
        'predano': '0',
        'predano_organizace': '1',
        'poradi': '-1',
        'ident_cely': '-1'
    }

    for k, v in params.items():
        allParams[k] = v

    return zmena(sessionId, 'detektor', keyword, allParams)


def delete_file(sessionId, fileId):

    resp = zmena(sessionId, 'soubor', 'delete', {'id': fileId})

    return resp

###########################################################################


def hledej_projekt(sessionId, params=None):
    logger.debug("xmlrpc.hledej projekt called")
    server = getServerAddr()

    allParams = {
        'date': '0',
        'do_akce': '',
        'oznamovatel_mod': '-1',
        'archivovane': '',
        'cislo_vyzkumu': '',
        'uzivatelske_oznaceni': '',
        'typ_projektove_dokumentace': '-1',
        'prihlasene': '',
        'okres': '-1',
        'nerevidovana_akce': '',
        'uzemni_kulturni_pamatky': '-1',
        'oznamovatel': '',
        'archivovana_akce': '',
        'katastr_akce': '-1',
        'termin_odevzdani_nz_do': '',
        'parcelni_cislo': '',
        'pristupnost_akce': '-1',
        'zaa_archivovana_akce': '',
        'limit': '100',
        'lokalita_mod': '-1',
        'registrovane': '',
        'datum_do': '',
        'organizace': '-1',
        'zahajene': '',
        'zrusene': '',
        'typ_akce': '-1',
        'nz_odlozena_akce': '',
        'prihlasene_sledovani': '',
        'navrzene_ke_zruseni_sledovani': '',
        'parcelni_cislo_mod': '-1',
        'stranka': '0',
        'druh_vyzkumu': '-1',
        'date_end': '',
        'datum_realizace_do': '',
        'odpovedny_pracovnik_zapisu': '',
        'navrzene_ke_zruseni': '',
        'vedouci_akce': '-1',
        'popisne_udaje_akce': '',
        'typ_projektu': '-1',
        'rok_od': '',
        'lokalita': '',
        'date_start': '',
        'oznamene': '',
        'popisne_udaje': '',
        'archivovane_sledovani': '',
        'sledovani_zmen_do': '',
        'odpovedny_pracovnik_prihlaseni': '-1',
        'ukoncene': '',
        'organizace_akce': '-1',
        'rozepsana_akce': '',
        'nazev_projektu': '',
        'navrzene_k_archivaci_sledovani': '',
        'admin': '',
        'registrovane_sledovani': '',
        'rok_do': '',
        'nz_vracena_akce': '',
        'nazev_projektu_mod': '-1',
        'od_akce': '',
        'uzivatel': '-1',
        'zahajene_sledovani': '',
        'zaa_k_archivaci_akce': '',
        'katastr': '-1',
        'order_ascending': 'asc',
        'stav': '',
        'kraj': '-1',
        'datum_od': '',
        'navrzene_k_archivaci': 'checked',
        'sledovani_zmen_od': '',
        'ukoncene_sledovani': '',
        'nz_odevzdana_akce': '',
        'zapsala_organizace': '-1',
        'termin_odevzdani_nz_od': '',
        'zaa_vracena_akce': '',
        'typ_kulturni_pamatky': '-1',
        'id_projektu': '-1',
        'prihlasila_organizace': '-1',
        'db_id_projektu': '-1',
        'order_by': 'katastr',
        'datum_realizace_od': '',
        'vedouci_projektu': '-1'
    }
    if(params is not None):
        for k, v in params.items():
            allParams[k] = v

    with xmlrpc.client.ServerProxy(server, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.hledej_projekt(sessionId, helper.create_parameters(allParams))
        return resp[2:]

#####################################################
#####################SOUBORY#########################
#####################################################

# Upload souboru k dokumentu


def pripoj_soubor_dokument(sessionId, idDokumentu, nazevSouboru, rozsah):
    logger.debug("xmlrpc.pripoj_soubor called %s, %s, %s, %s ", str(idDokumentu), str(nazevSouboru), str(rozsah), 'OSD')

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.pripoj_soubor(sessionId, idDokumentu, nazevSouboru, rozsah)
        if(resp[0]):
            return resp[1:]
        else:
            return None


def ukonci_pripojovani_souboru(sessionId, username, puvodniNazevSouboru, noveNazvy):
    logger.debug("xmlrpc.ukonci_pripojovani_souboru called %s, %s, %s ",
                 str(username), puvodniNazevSouboru, str(noveNazvy))

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.ukonci_pripojovani_souboru(sessionId, username, puvodniNazevSouboru, noveNazvy)
        if(resp[0]):
            return resp[1:]
        else:
            return None


def uploadDocumentFile(sessionId, dokument, f):
    rozsah = 1
    resp = pripoj_soubor_dokument(sessionId, dokument.id.id, f.name, rozsah)
    if (resp):
        hostname = resp[0]['hostname']
        username = resp[0]['username']
        password = resp[0]['password']

        # pocitam checksum
        checksum = helper.calculateCrc32(f.file)

        # Move read pointer to the beginnning of the file !!
        f.file.seek(0)
        ftp.uploadToFtpFile(hostname, username, password, f.name, f.file)
        print(str(f.name))
        finish_resp = ukonci_pripojovani_souboru(
            sessionId, username, f.name + ':' + checksum, [f.name + ':' + checksum])
        return finish_resp

    else:
        logger.debug("Připoj soubor dokument vratilo prázdnou odpověď")
        raise Exception('Připoj soubor dokument vratilo prázdnou odpověď')

# Download souboru z dokumentu


def stahni_soubor(sessionId, souborId):
    logger.debug("xmlrpc.stahni_soubor called %s", str(souborId))

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=True) as proxy:
        resp = proxy.stahni_soubor(sessionId, souborId)
        if(resp[0]):
            return resp[1:]
        else:
            return None


def ukonci_stahovani(sessionId, username):
    logger.debug("xmlrpc.ukonci_stahovani called %s", username)

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=True) as proxy:
        resp = proxy.ukonci_stahovani(sessionId, username)
        if(resp[0]):
            return resp[1:]
        else:
            return None


def downloadFile(sessionId, fileId):

    resp = stahni_soubor(sessionId, fileId)
    if (resp):
        hostname = resp[0]['hostname']
        username = resp[0]['username']
        password = resp[0]['password']
        fileName = resp[0]['soubor'][0].split(':')[0]

        f = ftp.downloadFromFtpFile(hostname, username, password, fileName)
        resp = ukonci_stahovani(sessionId, username)
        return fileName, f
    else:
        logger.debug("Soubor s id %s neexistuje.", str(fileId))
        raise Exception("Soubor s id %s neexistuje.", str(fileId))

# Upload souboru k projektu


def pripoj_soubor_projekty(sessionId, idProjektu, nazevSouboru, rozsah):
    logger.debug("xmlrpc.pripoj_soubor_projekty called %s, %s, %s , %s",
                 str(idProjektu), nazevSouboru, str(rozsah), 'FDN')

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.pripoj_soubor_projekty(sessionId, idProjektu, nazevSouboru, rozsah)
        if(resp[0]):
            return resp[1:]
        else:
            return None


def ukonci_pripojovani_souboru_projekty(sessionId, username, puvodniNazevSouboru, noveNazvy):
    logger.debug("xmlrpc.ukonci_pripojovani_souboru_projekty called %s, %s, %s ",
                 str(username), puvodniNazevSouboru, str(noveNazvy))

    with xmlrpc.client.ServerProxy(DEV_SERVER_ADDR, encoding="UTF-8", verbose=False) as proxy:
        resp = proxy.ukonci_pripojovani_souboru_projekty(sessionId, username, puvodniNazevSouboru, noveNazvy)
        if(resp[0]):
            return resp[1:]
        else:
            print(resp)
            return None

# V tomto kontextu jsou project files obrazky/fotky samostatnych nalezu


def uploadProjectFile(sessionId, projectId, f, nalez):

    # Protoze momentalne php server ani depozitar dokumentace nevi ze tento soubor byl uploadovan nalezcem samostatneho nalezu (jeho typ je FDN),
    # prejmenovani nastane jeste pred uploadem.

    # Prejmenovani je nasledovne:
    # [hash]_[ident_cely]F[##].xxx

    # ident_cely - identifikator nalezu ke kteremu fotografii uploaduju
    # [##] - poradove cislo souboru pro nalez
    # xxx - koncovka
    #
    # Notes: Hash je pridan depozitarem dokumentace volane metodou ukonci_pripojovani_souboru_projekty php servru
    extension = os.path.splitext(f.name)[1]
    connected_records = nalez.soubor_set.all()
    number = 0
    last_number_regex = re.compile(r"f\d+\.(?:jpg|jpeg|tiff|tif|png)")
    """
    This loop is used because data in database are corrupted and the last inserted number may not be the highest
    one. Thus, all connected records need to be checked.
    """
    for record in connected_records:
        last_file_name = record.nazev.lower()
        results = last_number_regex.findall(last_file_name)
        result: str = results[-1]
        current_number = result[1:result.find(".")]
        if current_number.isdigit() and int(current_number) > number:
            number = int(current_number)
    number += 1
    newName = nalez.ident_cely + 'F' + str(number) + extension
    f.name = newName

    rozsah = 1
    resp = pripoj_soubor_projekty(sessionId, projectId, f.name, rozsah)
    # print(resp)
    if (resp):
        hostname = resp[0]['hostname']
        username = resp[0]['username']
        password = resp[0]['password']

        # pocitam checksum
        checksum = helper.calculateCrc32(f.file)

        # Move read pointer to the beginnning of the file !!
        f.file.seek(0)

        ftp.uploadToFtpFile(hostname, username, password, f.name, f.file)
        finish_resp = ukonci_pripojovani_souboru_projekty(
            sessionId, username, f.name + ':' + checksum, [f.name + ':' + checksum])
        return finish_resp

    else:
        logger.debug("Připoj soubor dokument vratilo prázdnou odpověď")
        raise Exception('Připoj soubor dokument vratilo prázdnou odpověď')

#####################################################


def getServerAddr():
    if(settings.AMCR_BACKEND_MOCK):
        return MOCK_SERVER_ADDR
    else:
        return DEV_SERVER_ADDR
