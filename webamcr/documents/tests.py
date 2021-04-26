from django.test import TestCase
from . import xmlrpc
from .constants import AmcrConstants as constants
from . import helper
from django.conf import settings
from webamcr import helper_general
from .models import Dokument

#import html5lib
import json
import time
import threading
from shapely import wkb

# ******* Tests if the URLS give correct responses and that HTML is parsable *********


class TestUrls(TestCase):

    def setUp(self):
        settings.AMCR_BACKEND_MOCK = True

    # Success tests
    def test_documents(self):
        response = self.client.get('/documents/')
        self.assertEqual(response.status_code, 200)
        print(response.content)
        #parser = html5lib.HTMLParser(strict=True)
        # parser.parse(response.content)


class TestXMLRPCMockServer(TestCase):

    # ---- Mock server simple tests ----
    def setUp(self):
        settings.AMCR_BACKEND_MOCK = True

    # Checking that mocking server is returning something
    def test_login_response(self):
        response = xmlrpc.login('', '', '')
        self.assertEqual(response, 1)

    def test_get_current_info_response(self):
        response = xmlrpc.get_current_user('')
        self.assertEqual(response["email"], 'jurajskvarla@yahoo.com')

    def test_nacti_informace_list(self):
        response = xmlrpc.nacti_informace_list('', '', '')
        self.assertTrue(response)

    def test_hledej_dokument(self):
        response = xmlrpc.hledej_dokumenty_uzivatel('', '')
        self.assertTrue(response)

# ********* Tests related to RML RPC requests **********


class TestXMLRPCDevServer(TestCase):

    SID = 0

    def setUp(self):
        settings.AMCR_BACKEND_MOCK = False
        self.SID = xmlrpc.get_sid()
        print('User Juraj logged in with sid: ' + self.SID)
        self.assertTrue(xmlrpc.login(self.SID, 'juraj.skvarla@spacesystems.cz', 'aaa') == 1)
        #self.assertTrue(xmlrpc.login(self.SID, 'admin', 'heslo123') == 1)
        #self.assertTrue(xmlrpc.login(self.SID, 'jurajskvarla@yahoo.com', 'aaa') == 1)

    def test_aktualni_cas(self):
        response = xmlrpc.aktualni_cas(self.SID)
        print(response)

    def test_update_cooridinates(self):

        response = xmlrpc.zmena(self.SID, 'dokument', 'update', {
            'northing': 50.670727,
            'easting': 14.038081,
            'id': 742236
        })
        print(response)

    def test_mapovani_jmen(self):
        helper_general.get_user_name_from_id(self.SID, 741808)

    def test_session_validity(self):
        print(time.ctime())
        response = xmlrpc.get_current_user(self.SID)
        print(response)
        threading.Timer(5, self.test_session_validity).start()

    def test_hledej_dokument_of_juraj(self):
        # Retrieve sid
        sid = xmlrpc.get_sid()
        self.assertTrue(sid)

        # Get my user ID from the develop database
        jurajId = 741808
        response = xmlrpc.hledej_dokument(sid, {
            'uzivatel': str(jurajId)
        })
        ids = []
        for i in range(len(response)):
            if(i > 1):
                ids.append(response[i]['id'])

        self.assertTrue(len(ids) > 8)

    def test_get_user_info_not_logged_in(self):
        resp = xmlrpc.get_current_user(self.SID)
        print(resp)
        self.assertTrue(len(resp) == 0)

    def test_login_juraj(self):
        response = xmlrpc.login(self.SID, 'juraj.skvarla@spacesystems.cz', 'aaa')
        self.assertTrue(response == 1)

    def test_nacti_informace_list(self):
        response = xmlrpc.nacti_informace_list(self.SID, 'dokument', [742236])
        print(response)

    def test_login_and_get_current_user(self):
        xmlrpc.login(self.SID, 'juraj.skvarla@spacesystems.cz', 'aaa')
        response = xmlrpc.get_current_user(self.SID)
        self.assertTrue(response['id'] == 741808)

    def test_get_list_zachovalost(self):
        resp = xmlrpc.get_list(self.SID, constants.PRESERVATION)
        self.assertTrue(len(resp) == 6)

    def test_get_list_kataster_1(self):
        resp = xmlrpc.get_list(self.SID, constants.CADASTRE_1)
        self.assertTrue(len(resp) >= 7000)

    def test_get_list_kataster_2(self):
        resp = xmlrpc.get_list(self.SID, constants.CADASTRE_2)
        self.assertTrue(len(resp) > 6200)

    def test_get_series(self):
        resp = xmlrpc.get_list(self.SID, constants.SERIES)
        self.assertTrue(len(resp) > 14)

    def test_get_list_jmena(self):
        resp = xmlrpc.get_list(self.SID, 'jmena', 'prijmeni', 'jmeno')
        self.assertTrue(len(resp) > 0)

    def test_hledej_dokument_zachovalost_6(self):
        resp = xmlrpc.hledej_dokument(self.SID, {
            constants.PRESERVATION: '6',
        })
        # Nevraci to nic, nevim zda neni chyba na servru
        self.assertTrue(len(resp) == 0)

    def test_hledej_autor_id(self):
        resp = xmlrpc.get_autor_id(self.SID, 'Juraj', 'Skvarla')
        self.assertTrue(resp == 29824)

    def test_hledej_dokument_autor(self):
        resp = xmlrpc.hledej_dokument(self.SID, {
            'autor': '29772',  # 29820 = pavla, 29824 - ja, pavla na testu = 29772
        })
        self.assertTrue(len(resp) != 0)

    def test_hledej_dokument_odpovedny_pracovnik(self):
        resp = xmlrpc.hledej_dokument(self.SID, {
            'odpovedny_pracovnik_vlozeni': '2',
            'rada': '16'
        })
        self.assertTrue(len(resp) > 10)

    def test_hledej_dokument_rada(self):
        resp = xmlrpc.hledej_dokument(self.SID, {'rada': '16'})
        self.assertTrue(len(resp) > 10)

    def test_nacti_informace_dokument(self):
        resp = xmlrpc.nacti_informace(self.SID, 'dokument', 742236)
        print(json.dumps(resp, indent=2))

    def test_get_documents_raw(self):
        resp = xmlrpc.hledej_dokument_raw(self.SID, 'typ=-1&pristupnost=-1&typ_dokumentu=-1&rada=-1&stav=-1&id_cj=-1&')
        print(len(resp))

    def test_get_models_3D(self):
        resp = xmlrpc.hledej_dokument(self.SID, {'rada': '16'})
        self.assertTrue(len(resp) >= 2)

    def test_get_typ_dokumentu_for_3D(self):
        resp = xmlrpc.get_list_3D_model_type_form(self.SID, 'typ_dokumentu')
        self.assertTrue(len(resp) == 2)

    def test_get_format_dokumentu_for_3D(self):
        resp = xmlrpc.get_list_3D_model_type_form(self.SID, 'format_dokumentu')
        self.assertTrue(len(resp) == 3)

    def test_get_model(self):
        resp = xmlrpc.nacti_informace_list(self.SID, 'dokument', [741907])
        print(json.dumps(resp, indent=1))

    def test_get_sumarizace(self):
        resp = xmlrpc.get_sumarizace(self.SID)
        print(json.dumps(resp, indent=1))

    def test_nacti_vazby_soubory(self):
        resp = xmlrpc.nacti_vazby(self.SID, 'dokument_soubor', 741907)
        print(json.dumps(resp, indent=1))

    def test_nacti_vazby_na_dokument(self):
        resp = xmlrpc.nacti_vazby(self.SID, 'vazby_na_dokument', 741907)
        print(json.dumps(resp, indent=1))

    def test_nacti_vazby_odkaz(self):
        resp = xmlrpc.nacti_vazby(self.SID, 'odkaz', 741907)
        print(json.dumps(resp, indent=1))

    def test_hlede_akce_dokumentu(self):
        resp = xmlrpc.hledej_akce_dokumentu(self.SID, 741907, {})
        self.assertTrue(resp[0]['id'] == 741949)

    def test_nacti_model_all(self):
        resp = xmlrpc.get_model_detail_tree(self.SID, 741907)

    def test_archivace_modelu(self):
        resp_user = xmlrpc.get_current_user(self.SID)
        resp = xmlrpc.zmena(self.SID, 'dokument', 'update', {
            'archivovat_dokument': '1',
            'odpovedny_pracovnik_archivace': str(resp_user['id']),
            'datum_archivace': helper.getCurrentEpochTime(),
            'id': '741921',
        })

    def test_get_archeologist_id(self):

        id_admin = helper.get_archeologist_id(self.SID, 'juraj.skvarla@spacesystems.cz')

        self.assertTrue(id_admin != -1)

        id_archeo = helper.get_archeologist_id(self.SID, 'pavla_archeolog@example.com')

        self.assertTrue(id_archeo != -1)

        id_archiva = helper.get_archeologist_id(self.SID, 'pavla_archivar@example.com')

        self.assertTrue(id_archiva != -1)

    def test_create_3D_model(self):
        resp = xmlrpc.create_update_3D_model(self.SID, 'create', {
            'typ_dokumentu': '43',
            'autor': 'Skvarla, Juraj',
            'organizace_autora': '315744',
            'format': '15',
            'rok_vzniku': '2016',
            'duveryhodnost': '78',
            'oznaceni_originalu': 'Libovolny text',
            'popis': 'Nejaky povinny popis',
            # DODATECNE INFO
            'poznamka': '',
            'odkaz': '',
            # LOKALIZACE OBSAHU
            'pas': '',
            'northing': '',
            'easting': '',
            'zeme': '',
            'region': '',
        })

        print(resp)
        self.assertTrue(resp[0] == True)

    def test_update_3D_model(self):
        model_id = '741969'
        resp = xmlrpc.create_update_3D_model(self.SID, 'update', {
            'id': model_id,
            'typ_dokumentu': '43',
            'autor': 'Skvarla, Juraj',
            'organizace_autora': '315744',
            'format': '15',
            'rok_vzniku': '2016',
            'duveryhodnost': '78',
            'oznaceni_originalu': 'Libovolny text',
            'popis': 'Nejaky povinny popis',
            # DODATECNE INFO
            'poznamka': '',
            'odkaz': '',
            # LOKALIZACE OBSAHU
            'pas': '',
            'northing': '',
            'easting': '',
            'zeme': '',
            'region': '',
            # NAVIC required
            #'ulozeni_originalu': '5',
        })

        print(resp)

    def test_get_current_epoch_timestamp(self):
        print(str(int(helper.getCurrentEpochTime())))

    def test_delete_dokument(self):

        idToDelete = 741955
        resp = xmlrpc.zmena(self.SID, 'dokument', 'delete', {
            'id': str(idToDelete)
        })
        print(resp)

    def test_stahni_soubor(self):

        resp = xmlrpc.downloadFile(self.SID, 783)

        print(resp)

    def test_delete_file(self):

        xmlrpc.delete_file(self.SID, 852)

    # def test_pripoj_soubor_dokument_741907(self):
    #   idDoukemntu = 741907
    #   nazevSouboru = 'image.png'
    #   filePath = 'C:/Users/'
    #   rozsah = 2
    #   resp = xmlrpc.pripoj_soubor_dokument(self.SID, idDoukemntu ,nazevSouboru, rozsah)
    #   print(resp)
    #   if (len(resp) != 0):
    #       hostname = resp[0]['hostname']
    #       username = resp[0]['username']
    #       password = resp[0]['password']
    #       #pocitam checksum
    #       checksum = helper.calculateCrc32(filePath + nazevSouboru)

    #       ftp.uploadToFtp(hostname, username, password, filePath, nazevSouboru)

    #       resp2 = xmlrpc.ukonci_pripojovani_souboru(self.SID, username, nazevSouboru + ':' + checksum, [nazevSouboru + ':' + checksum])
    #       print(resp2)

    #   else:
    #       print("Připoj soubor dokument vratilo prázdnou odpověď")

    #   print(str(resp))

    # def test_pripoj_soubor_document_hardcode(self):
    #   hostname = 'api-dev.archeologickamapa.cz'
    #   username = '2bf10a699fbcbb0dcd52640be00fcc68cff4bf4b'
    #   password = '57e50a9679ad74df7738a1938bc0b138f19a8722'
    #   nazevSouboru = 'image.png'
    #   filePath = 'C:/Users/'

    #   ftp.uploadToFtp(hostname, username, password, filepath, nazevSouboru)

    # def test_ukonci_pripojovani(self):
    #   sId = 'bjl4n641equk1805pbstnp4b81'
    #   username = '2a65e6ac5c9d15ae3dc92fce316cc0f28d888219'
    #   puvodniNazevSouboru = 'image.png'
    #   noveNazvy = 'juraj.png'
    #   resp = xmlrpc.ukonci_pripojovani_souboru(sId, username, puvodniNazevSouboru, noveNazvy)
    #   print(resp)

    # def test_nacti_checksum(self):
    #   prev = 0
    #   for eachLine in open('C:/Users/image.png',"rb"):
    #       prev = zlib.crc32(eachLine, prev)

    #   checksum = "%d"%(prev & 0xFFFFFFFF)

    #   self.assertEqual(checksum == 3841995988)


# *********  Other tests ***********
class TestPythonServer(TestCase):

    def test_set_query_parameter(self):
        qpar = xmlrpc.QParameters()
        qpar.setParam('id_cj', 'testing')
        qparam = qpar.getParams()
        self.assertTrue('aktivita=-1&areal_druha=&typ=-1&okres=-1&typ_nalezu=-1&rok_vzniku=-1&lokalizace_nazev_lokality_mod=' +
                        '&popis_udalosti=&pristupnost=-1&limit=100&typ_dokumentu=-1&organizace=-1&dokumenty_typ=&db_id_dokumentu=-1&obdobi_od=-1' +
                        '&typ_udalosti=-1&stranka=0&specifikace_predmet=-1&autor=-1&rok_od=&rok_do=&dokumenty_id=&dokumenty_rada=&dokumenty_autor_mod=' +
                        '&nalez_predmet_druha=-1&dokumenty_popis_mod=&dokumenty_rok_vzniku=&lokalizace_nazev_lokality=&zachovalost=-1&obdobi_nadrazene=-1' +
                        '&specifikace_zahrnute=-1&obdobi_zahrnute=-1&areal_zahrnute=&uzivatel=-1&rada=-1&nalez_objekt_druha=-1&katastr=-1&order_ascending=asc' +
                        '&specifikace_objekt=-1&kraj=-1&dokumenty_organizace=&areal_prvni=&popis=&dokumenty_popis=&obdobi_do=-1&dokumenty_autor=&order_by=typ_dokumentu' +
                        '&nalez_zahrnute=-1&id_cj=testing&stav=-1&' == qparam)

    def test_params_split_two(self):

        parameters = 'id_cj=ABCDEF&typ_dokumentu=-1&'

        parsed = helper.parse_parameters(parameters)
        self.assertTrue(parsed['id_cj'] == 'ABCDEF')

    def test_params_split_one(self):

        parameters = 'uzivatel=123456'

        parsed = helper.parse_parameters(parameters)
        print(parsed)
        self.assertTrue(parsed['uzivatel'] == '123456')


# Jméno uživ. skupiny    kód   kód binárně  Označení v hesláři Přístupnost
# anonym                  0     0                     A
# badatel                 1     1                     B
# archeolog               2     10                    C
# archivář                16    10000                 D
# administrátor           4     100                   E
# user admin              8                           Oprávnění (de)aktivovat uživatele

#  --------------- OPRAVNENI --------------
#  archivar detektoru     32
#  spravce uctu           64
#  spravce 3D             128

    def test_get_roles_and_permissions(self):

        authLevel = 129  # (spravce 3D + badatel)

        authLevelResp = {
            'opravneni': [],
        }

        if((authLevel & 1) == 1):
            authLevelResp['role'] = 'Badatel'
        elif((authLevel & 2) == 2):
            authLevelResp['role'] = 'Archeolog'
        elif((authLevel & 4) == 4):
            authLevelResp['role'] = 'Admin'
        elif((authLevel & 16) == 16):
            authLevelResp['role'] = 'Archivář'
        else:
            authLevelResp['role'] = 'Anonym'

        if((authLevel & 128) == 128):
            authLevelResp['opravneni'].append('Správce 3D')

        self.assertTrue(authLevelResp['role'] == 'Badatel')

    def test_store_constants(self):

        helper.dump_cached_data_to_file()

    def test_load_constants(self):

        helper.load_cached_data_from_file()

    def test_point_to_coordinates_extraction(self):

        exp_nort = 50.034209
        exp_east = 14.414063
        coordhex = '0101000020E6100000A1F7C61000D42C404B1DE4F560044940'
        point = wkb.loads(coordhex, hex=True)
        x = point.x
        y = point.y

        self.assertEqual(exp_nort, y)
        self.assertEqual(exp_east, x)

        coordhex = ''
        if coordhex:
            point = wkb.loads(coordhex, hex=True)
            print(str(point))
        else:
            print("empty coordinaltes")

    def test_brute_force(self):
        uzivatele = ['juraj.skvarla@spacesystems.cz']
        your_list = 'abcdefghijklmnopqrstuvwxyz'
        SID = xmlrpc.get_sid()
        complete_list = []
        for current in range(3):
            a = [i for i in your_list]
            for y in range(current):
                a = [x + i for i in your_list for x in a]
            complete_list = complete_list + a

        #print(complete_list)
        for case in complete_list:
        	response = xmlrpc.login(SID, uzivatele[0], case)
        	print(case + " - " + str(response))


    def test_user_permissions(self):

        user = {}
        user['auth'] = 204

        permission = constants.USERS_ADMIN
        group = constants.ADMIN

        canAccess = helper.check_user_group_and_permission(user, group, permission)
        self.assertTrue(canAccess is True)

        user['auth'] = 196
        canAccess = helper.check_user_group_and_permission(user, group, permission)
        self.assertTrue(canAccess is False)
