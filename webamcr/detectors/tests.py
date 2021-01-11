
import django_rq
import time

from django.conf import settings
from django.db.models import Q
from django.test import TestCase, RequestFactory
from documents.constants.AmcrConstants import CADASTRE_12_CACHE, CADASTRE_1_CACHE, CADASTRE_2_CACHE
from detectors.views import create

from documents import xmlrpc

from .models import Projekt, VazbaSpoluprace


class TestXMLRPCDevServer(TestCase):
    SID = 0

    def setUp(self):
        settings.AMCR_BACKEND_MOCK = False
        self.SID = xmlrpc.get_sid()
        self.assertTrue(xmlrpc.login(self.SID, 'juraj.skvarla@spacesystems.cz', 'aaa') == 1)

    def test_delete_detector(self):
        idToDelete = 19
        resp = xmlrpc.zmena(self.SID, 'detektor' , 'delete', {
            'id': str(idToDelete)
            })
        print(resp)

    @staticmethod
    def test_find_projects():

        badatel_id = 741804
        spoluprace = VazbaSpoluprace.objects.filter(badatel=741804, aktivni=True, potvrzeno=True)
        # Example of how to retrive Detector related projects
        projekty = Projekt.objects.filter((Q(stav=3) | Q(stav=4)) & Q(typ_projektu=3))

        print(projekty)

    def sent_test_email(self):

        print("email sent: " + str(ret))

    def test_kataster(self):

        print("Test access time of the cataster object")

        dict_cad = dict(CADASTRE_12_CACHE)

        # Searching through list
        print(len(CADASTRE_12_CACHE))
        counter = 0
        start_time = time.time()
        for item in CADASTRE_12_CACHE:
            counter+= 1
            if item[0] == 328839:
                break

        print(counter)
        print("--- %s seconds ---" % (time.time() - start_time))


    #Request testing
    def test_login_page(self):
        self.SID = xmlrpc.get_sid()
        self.assertTrue(xmlrpc.login(self.SID, 'juraj.skvarla@spacesystems.cz', 'aaa') == 1)

        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_create_page(self):
        SID = xmlrpc.get_sid()
        self.assertTrue(xmlrpc.login(SID, 'juraj.skvarla@spacesystems.cz', 'aaa') == 1)

        request = RequestFactory().get('/pas/create')
        request.COOKIES['sessionId'] = SID
        response = create(request)
        print(request)
        print(response)
        self.assertEqual(response.status_code, 200)

