import logging

from django.conf import settings
from django_rq import job
from django.core.mail import send_mail
from documents.constants import AmcrConstants as amcr_c
from .constants import DetectorConstants as c
from .models import Organizace, UserStorage

logger = logging.getLogger(__name__)

_from = 'info@amapa.cz'
notice_footer = 'Toto je automaticky generovaná zpráva systému AMČR. V případě potřeby kontaktujte administrátora ARÚ Praha (amcr@arup.cas.cz) nebo ARÚ Brno (amcr@arub.cz). Odesláno z ' + \
    settings.DOMAIN_NAME + '.'


@job
def email_send_SN1(user, nalez, target_email):
    logger.debug('Preparing SN1 email to archeolog to notify him about new finding in state N2')

    name = user.jmeno
    surname = user.prijmeni

    target_user = UserStorage.objects.get(email=target_email)
    notification = target_user.notifikace_nalezu

    subject = "AMČR-PAS: Nový samostatný nález ke schválení"
    content = 'Dobrý den,<br>v AMČR-PAS byl dnes Vaším spolupracovníkem' + ' ' + name + ' ' + \
        surname + ' odeslán nový nález (<strong>' + nalez.ident_cely + '</strong>) ke schválení.<br><br>'
    content += 'Detaily zjistíte po přihlášení do AMČR-PAS.<br><br>'
    content += notice_footer

    if notification:
        ret = send_mail(
            subject,  # Subject
            "",  # Content
            _from,  # From
            [target_email],  # To
            html_message=content
        )

        return ret
    else:
        logger.debug("Notification SN1 to user " + target_email + " not sent. User notification setting off.")
    return 0


@job
def email_send_SN2(nalez, target_email):
    logger.debug('Preparing email SN2 to badatel to notify him about his findings being archived')

    subject = "AMČR-PAS: Váš nález byl archivován"
    content = 'Dobrý den,<br><br>v AMČR-PAS byl dnes archivován Vámi přidaný nález <strong>' + nalez.ident_cely + '</strong>.<br><br>'
    content += 'Detaily zjistíte po přihlášení do AMČR-PAS. Nejpozději během následujícího dne budou informace o nálezu zvěřejněny v Digitálním archivu AMČR.<br><br>'
    content += notice_footer

    target_user = UserStorage.objects.get(email=target_email)
    notification = target_user.notifikace_nalezu

    if notification:
        ret = send_mail(
            subject,  # Subject
            "",  # Content
            _from,  # From
            [target_email],  # To
            html_message=content
        )

        return ret
    else:
        logger.debug("Notification SN2 to user " + target_email + " not sent. User notification setting off.")
    return 0


@job
def email_send_SN3andSN4(nalez, target_email, novy_stav, duvod):
    logger.debug('Preparing email SN3 or SN4 to badatel when additional info or correction is required')

    target_user = UserStorage.objects.get(email=target_email)
    notification = target_user.notifikace_nalezu

    katastr = c.UNKNOWN
    for item in amcr_c.CADASTRE_12_CACHE:
        if item[0] == nalez.katastr:
            katastr = item[1]

    stav = c.UNKNOWN
    for item in c.DETECTOR_STATE_CACHE:
        if item[0] == novy_stav:
            stav = item[1]

    subject = 'AMČR-PAS: samostatný nález ' + nalez.ident_cely + ' vrácen k doplnění'
    content = 'Dobrý den,<br><br>vámi odeslaný samostatný nález <strong>' + nalez.ident_cely + \
        '</strong> na katastru <strong>' + katastr + '</strong> byl vrácen do stavu <strong>' + stav + '</strong>.<br><br>'

    content += '<strong>Důvod:</strong> ' + duvod + '<br><br>'
    content += 'Detaily zjistíte po přihlášení do AMČR-PAS.<br><br>'
    content += notice_footer

    if notification:
        ret = send_mail(
            subject,  # Subject
            "",  # Content
            _from,  # From
            [target_email],  # To
            html_message=content
        )

        return ret
    else:
        logger.debug("Notification SN3/4 to user " + target_email + " not sent. User notification setting off.")
    return 0


@job
def email_send_SN5(host, user, target_email, cooperation):
    logger.debug("Preparing email SN5 to archeologist when new cooperation has been requested.")

    org_list = Organizace.objects.values_list('id', 'nazev_zkraceny', named=True)
    organizace = org_list.get(pk=user.organizace.id).nazev_zkraceny

    id_uzivatele = user.id.id
    name = user.jmeno
    surname = user.prijmeni
    email = user.email
    telefon = user.telefon

    target_user = UserStorage.objects.get(email=target_email)
    notification = target_user.notifikace_nalezu

    subject = 'AMČR-PAS: nový spolupracovník'
    content = 'Dobrý den,<br><br>nový uživatel žádá o zařazení mezi spolupracovníky:<br><br>'
    content += 'ID: ' + str(id_uzivatele) + '<br>Jméno: ' + name + '<br>Příjmení: ' + surname + \
        '<br>Organizace: ' + organizace + '<br>Email (přihlašovací jméno): ' + email + '<br>Telefon: ' + telefon

    content += '<br><br>Spolupráci potvrdíte po přihlášení do AMČR-PAS, nebo kliknutím na tento odkaz:<br><br>'
    content += 'https://' + settings.DOMAIN_NAME + '/login/?next=/pas/cooperate/update/' + str(cooperation.id) + '\n\n'
    content += notice_footer

    if notification:
        ret = send_mail(
            subject,  # Subject
            "",  # Content
            _from,  # From
            [target_email],  # To
            html_message=content
        )

        return ret
    else:
        logger.debug("Notification SN5 to user " + target_email + " not sent. User notification setting off.")
    return 0


@job
def email_send_SN7(user, target_email):
    logger.debug("Preparing email SN7 when request for cooperation has been confirmed.")

    org_list = Organizace.objects.values_list('id', 'nazev_zkraceny', named=True)
    organization = org_list.get(pk=user.organizace.id).nazev_zkraceny

    name = user.jmeno
    surname = user.prijmeni
    email = user.email
    telefon = user.telefon

    target_user = UserStorage.objects.get(email=target_email)
    notification = target_user.notifikace_nalezu

    subject = 'AMČR-PAS: spolupráce potvrzena'
    content = 'Dobrý den,<br><br>spolupráce s uživatelem <strong>' + name + ' ' + surname + \
        '</strong> (<strong>' + organization + '</strong>) ' + 'byla úspěšně potvrzena.<br><br>'
    content += 'Jméno: ' + name + '<br>Příjmení: ' + surname + '<br>Organizace: ' + \
        organization + '<br>Email: ' + email + '<br>Telefon: ' + telefon
    content += '<br><br>Detaily o spolupráci získate po přihlášení do AMČR-PAS<br><br>'
    content += notice_footer

    if notification:
        ret = send_mail(
            subject,  # Subject
            "",  # Content
            _from,  # From
            [target_email],  # To,
            html_message=content
        )

        return ret
    else:
        logger.debug("Notification SN7 to user " + target_email + " not sent. User notification setting off.")
    return 0
