from django.shortcuts import render, redirect
from django.contrib import messages

from documents.constants import AmcrConstants as c
from documents import helper, xmlrpc
from documents.decorators import login_required
from documents import models as m
from detectors import models as dm
from django.utils import translation

import logging

logger = logging.getLogger(__name__)


@login_required
def home(request, **kwargs):

	isLogged, userDict = helper.is_user_logged_in(request)
	if(not isLogged):
		return redirect('login')

	return render(request, 'home.html')


def err_sid(request, *args, **argv):
	response = render(request, '403.html')
	response.status_code = 403
	return response


@login_required
def delete(request, fileId, **kwargs):

	sid = request.COOKIES.get('sessionId')

	resp = xmlrpc.delete_file(sid, fileId)

	if not resp[0]:
		# Not sure if 404 is the only correct option
		messages.add_message(request, messages.SUCCESS, c.OBEJCT_COULD_NOT_BE_DELETED)
		return render(request, 'error_404.html')
	else:
		logger.debug("Byl smazán soubor s id: " + str(fileId))
		messages.add_message(request, messages.SUCCESS, c.OBJECT_DELETED_SUCCESSFULLY)

	return redirect(request.META['HTTP_REFERER'])


# Heslare
def heslar_pristupnost():
	language = translation.get_language()
	tuples = [('', '')]
	ADMIN_ID = 5
	if language == 'cs':
		p = m.HeslarPristupnost.objects.all().exclude(id=ADMIN_ID).values('id', 'vyznam')
		tuples += [(q['id'], q['vyznam']) for q in p]
	elif language == 'en':
		p = m.HeslarPristupnost.objects.all().exclude(id=ADMIN_ID).values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_organizace():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = dm.Organizace.objects.all().order_by('nazev_zkraceny').values('id', 'nazev_zkraceny')
		tuples += [(q['id'], q['nazev_zkraceny']) for q in p]
	elif language == 'en':
		p = dm.Organizace.objects.all().order_by('en').values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_zeme():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.HeslarZeme.objects.all().order_by('poradi').values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = m.HeslarZeme.objects.all().order_by('poradi').values('id', 'nazev_en')
		tuples += [(q['id'], q['nazev_en']) for q in p]
	return tuples


def heslar_spz_storage():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.SpzStorage.objects.all().values('id', 'full_name')
		tuples += [(q['id'], q['full_name']) for q in p]
	elif language == 'en':
		p = m.SpzStorage.objects.all().values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_specifikace_predmetu():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.HeslarSpecifikacePredmetu.objects.all().order_by('poradi').values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = m.HeslarSpecifikacePredmetu.objects.all().order_by('poradi').values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_typ_nalezu():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.HeslarTypNalezu.objects.all().values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = m.HeslarTypNalezu.objects.all().values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_format_dokumentu():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.HeslarFormatDokumentu.objects.filter(model=True).values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = m.HeslarFormatDokumentu.objects.filter(model=True).values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_typ_dokumentu():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = m.HeslarTypDokumentu.objects.filter(model=True).order_by('poradi').values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = m.HeslarTypDokumentu.objects.filter(model=True).order_by('poradi').values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_nalezove_okolnosti():
	language = translation.get_language()
	tuples = [('', '')]
	if language == 'cs':
		p = dm.HeslarNalezoveOkolnosti.objects.all().order_by('poradi').values('id', 'nazev')
		tuples += [(q['id'], q['nazev']) for q in p]
	elif language == 'en':
		p = dm.HeslarNalezoveOkolnosti.objects.all().order_by('poradi').values('id', 'en')
		tuples += [(q['id'], q['en']) for q in p]
	return tuples


def heslar_objekt_12():
	language = translation.get_language()
	translated_column = ''
	if language == 'cs':
		translated_column = 'nazev'
	else:
		translated_column = 'en'
	druhy = m.HeslarObjektDruh.objects.all().order_by('poradi').values('id', 'prvni', translated_column)
	kategorie = m.HeslarObjektKategorie.objects.all().order_by('poradi').values('id', translated_column)
	return mergeHeslare(kategorie, druhy, translated_column)


def heslar_predmet_12():
	language = translation.get_language()
	translated_column = ''
	if language == 'cs':
		translated_column = 'nazev'
	else:
		translated_column = 'en'
	druhy = m.HeslarPredmetDruh.objects.all().order_by('poradi').values('id', 'prvni', translated_column)
	kategorie = m.HeslarPredmetKategorie.objects.all().order_by('poradi').values('id', translated_column)
	return mergeHeslare(kategorie, druhy, translated_column)


def heslar_obdobi_12():
	language = translation.get_language()
	translated_column = ''
	if language == 'cs':
		translated_column = 'nazev'
	else:
		translated_column = 'en'
	druhy = m.HeslarObdobiDruha.objects.all().order_by('poradi').values('id', 'prvni', translated_column)
	kategorie = m.HeslarObdobiPrvni.objects.all().order_by('poradi').values('id', translated_column)
	return mergeHeslare(kategorie, druhy, translated_column)


def heslar_areal_12():
	language = translation.get_language()
	translated_column = ''
	if language == 'cs':
		translated_column = 'nazev'
	else:
		translated_column = 'en'
	druhy = m.HeslarArealDruha.objects.all().order_by('poradi').values('id', 'prvni', translated_column)
	kategorie = m.HeslarArealPrvni.objects.all().order_by('poradi').values('id', translated_column)
	return mergeHeslare(kategorie, druhy, translated_column)


def heslar_specifikace_objektu_12():
	language = translation.get_language()
	translated_column = ''
	if language == 'cs':
		translated_column = 'nazev'
	else:
		translated_column = 'en'
	druhy = m.HeslarSpecifikaceObjektuDruha.objects.all().order_by('poradi').values('id', 'prvni', translated_column)
	kategorie = m.HeslarSpecifikaceObjektuPrvni.objects.all().order_by('poradi').values('id', translated_column)
	return mergeHeslare(kategorie, druhy, translated_column)


def mergeHeslare(first, second, translated_column):
	data = [('', '')]
	for k in first:
		nazev_kategorie = k[translated_column]
		druhy_kategorie = []
		for druh in second:
			if druh['prvni'] == k['id']:
				druhy_kategorie.append((druh['id'], druh[translated_column]))
		data.append((nazev_kategorie, tuple(druhy_kategorie)))
	return data
