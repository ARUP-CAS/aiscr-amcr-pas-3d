import time
import logging

from documents import xmlrpc
from detectors import models
from django.shortcuts import get_object_or_404
from .constants import DetectorConstants as c
from . import amcemails as emails

logger = logging.getLogger(__name__)

# Transactions of the samostatne nalezy


def zapsani(params, user, sid):

	logger.debug("Zapsani nalezu")

	params['datum_vlozeni'] = str(int(time.mktime(time.localtime())))
	params['odpovedny_pracovnik_vlozeni'] = user.id.id
	params['stav'] = '1'
	# Create through xmlrpc
	resp = xmlrpc.create_update_detektor(sid, 'create', params)

	if resp[0]:
		id_det = str(resp[1])
		# And then load it using models
		nalez = get_object_or_404(models.SamostatnyNalez, pk=id_det)

		# Zapis zmen do historie
		zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ZAPSANI,
			samostatny_nalez = nalez,
			uzivatel = user
			)
		zmena.save()

		return nalez
	return None


def update(params, nalez, user, sid):

	logger.debug("Aktualizace nalezu : " + str(nalez.id))

	resp = xmlrpc.create_update_detektor(sid, 'update', params)

	if resp[0]:
		zmena = models.HistorieSamNalezu(
				typ_zmeny=c.AKTUALIZACE,
				samostatny_nalez = nalez,
				uzivatel = user
			)
		zmena.save()

	return resp


def odeslani(params, nalez, user, sid):

	logger.debug("Odeslani nalezu : " + str(nalez.id))

	params['stav']= c.ODESLANY

	resp = xmlrpc.create_update_detektor(sid, 'update', params)

	if resp[0]:
		zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ODESLANI,
			samostatny_nalez = nalez,
			uzivatel = user
		)
		zmena.save()
		project_id = nalez.projekt
		project = models.Projekt.objects.get(pk=project_id)
		if project.odpovedny_pracovnik_prihlaseni:
			emails.email_send_SN1.delay(user, nalez, project.odpovedny_pracovnik_prihlaseni.email)
		else:
			logger.error("Neexistuje odpovědný pracovník přihlášení projektu " + str(project_id))

	return resp


def potvrzeni(params, nalez, user, sid):

	logger.debug("Potvrzeni nalezu : " + str(nalez.id))

	params['stav']= c.POTVRZENY

	resp = xmlrpc.create_update_detektor(sid, 'update', params)

	if resp[0]:
		zmena = models.HistorieSamNalezu(
			typ_zmeny=c.POTVRZENI,
			samostatny_nalez = nalez,
			uzivatel = user
			)
		zmena.save()
		# Send email?

	return resp

def archivace(params, nalez, user, sid):

	logger.debug("Archivace nalezu : " + str(nalez.id))

	params['datum_archivace'] = str(int(time.mktime(time.localtime())))
	params['stav']= c.ARCHIVOVANY
	params['odpovedny_pracovnik_archivace']=str(user.id.id)

	resp = xmlrpc.create_update_detektor(sid, 'update', params)

	if resp[0]:
		zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ARCHIVACE,
			samostatny_nalez = nalez,
			uzivatel = user
			)
		zmena.save()
		zapsani_rec = nalez.historiesamnalezu_set.filter(typ_zmeny=c.ZAPSANI).last()
		if zapsani_rec:
			emails.email_send_SN2.delay(nalez, zapsani_rec.uzivatel.email)
		else:
			logger.error("Samostatný nález nemá odpovídající záznam o vytvoření v tabulce historie nálezů " + nalez.ident_cely)
	return resp


# Funkce dela to same jako funkce vraceni_k_odeslani ale nemeni stav nalezu pomoci xmlrpc ale primo v databazi
def vraceni_k_odeslani(user, finding, reason):

	finding.stav = c.ZAPSANY
	ret = finding.save(update_fields=["stav"]) # Must do like this because of the geom field which is not text

	#print(ret)
	zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ZPET_K_ODESLANI,
			samostatny_nalez = finding,
			uzivatel = user,
			duvod = reason
			)
	hist_ret = zmena.save()
	#print(hist_ret)

	# Podivam se do historie a najdu posledni odeslani
	odeslani_record = finding.historiesamnalezu_set.filter(typ_zmeny=c.ODESLANI).order_by('datum_zmeny').last()
	uzivatel_email = ''
	if odeslani_record:
		uzivatel_email = odeslani_record.uzivatel.email
	else:
		logger.error('Samostatny nalez '+ finding.ident_cely + ' nema zaznam o jeho odeslani v jeho historii')

	# Send email to the badatel that some corrections are required
	emails.email_send_SN3andSN4.delay(finding, uzivatel_email, c.ZAPSANY, reason)

	return ret

# Funkce dela to same jako funkce vraceni_k_odeslani ale nemeni stav nalezu pomoci xmlrpc ale primo v databazi
def vraceni_k_potvrzeni(user, finding, reason):

	finding.stav = c.ODESLANY
	ret = finding.save(update_fields=["stav"]) # Must do like this because of the geom field which is not text

	#print(ret)
	zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ZPET_K_POTVRZENI,
			samostatny_nalez = finding,
			uzivatel = user,
			duvod = reason
			)
	hist_ret = zmena.save()
	#print(hist_ret)

	# Podivam se do historie a najdu posledni odeslani
	record = finding.historiesamnalezu_set.filter(typ_zmeny=c.POTVRZENI).order_by('datum_zmeny').last()
	uzivatel_email = ''
	if record:
		uzivatel_email = record.uzivatel.email
	else:
		logger.error('Samostatny nalez '+ finding.ident_cely + ' nema zaznam o jeho potvrzeni v jeho historii')

	# Send email to the badatel that some corrections are required
	emails.email_send_SN3andSN4.delay(finding, uzivatel_email, c.ODESLANY, reason)

	return ret


def vraceni_k_archivaci(user, finding, reason):

	finding.stav = c.POTVRZENY
	ret = finding.save(update_fields=["stav"]) # Must do like this because of the geom field which is not text

	zmena = models.HistorieSamNalezu(
			typ_zmeny=c.ZPET_K_ARCHIVACI,
			samostatny_nalez = finding,
			uzivatel = user,
			duvod = reason
			)
	hist_ret = zmena.save()

	return ret
