
from django.utils.translation import gettext_lazy as _
from dataclasses import dataclass


@dataclass(frozen=True)
class AmcrConstants:
    AMCR_VERSION = '1.0.0'

    BOOL_CHOICES = ((True, _('Ano')), (False, _('Ne')))
    BOOL_WITH_BOTH_CHOICES = ((-1, ''), (True, _('Ano')), (False, _('Ne')))

    # Metis menu item identifiers
    MENU_LIBRARY = "menu_library"
    MENU_HOME_3D = "menu_home_3d"
    MENU_CREATE_3D = "men_create_3d"
    MENU_LIST_3D = "menu_list_3d"
    MENU_CHOOSE_3D = "menu_choose_3d"
    MENU_MANAGE_3D = "menu_manage_3d"

    MENU_DETECTORS = "menu_detectors"
    MENU_HOME_DET = "menu_home_det"
    MENU_CREATE_DET = "menu_create_det"
    MENU_LIST_DET = "menu_list_det"
    MENU_CHOOSE_DET = "mneu_choose_det"
    MENU_CONFIRM_DET = "menu_confirm_det"
    MENU_ARCHIVE_DET = "menu_archive_det"

    MENU_ADMINISTRATION = "menu_adimistration"
    MENU_ADMIN_USERS = "menu_users"

    # USER GROUPS/ROLES
    ADMIN = "Admin"
    ARCHEOLOG = "Archeolog"
    ARCHIVAR = "Archivář"
    BADATEL = "Badatel"
    NEAKTIVNI_UZIVATEL = "Neaktivní uživatel"

    ADMIN_ID = 1
    ARCHIVAR_ID = 2
    ARCHEOLOG_ID = 3
    BADATEL_ID = 4
    NEAKTIVNI_UZIVATEL_ID = 5

    MODELY_DOCUMENTS_ID = 16

    # User group sets
    USER_GROUP_SET_MIN_ADMIN = {ADMIN}
    USER_GROUP_SET_MIN_ARCHIVAR = {ADMIN, ARCHIVAR}
    USER_GROUP_SET_MIN_ARCHEOLOG = {ADMIN, ARCHIVAR, ARCHEOLOG}
    USER_GROUP_SET_MIN_BADATEL = {ADMIN, ARCHIVAR, ARCHEOLOG, BADATEL}
    USER_GROUP_SET_MIN_ANONYM = {ADMIN, ARCHIVAR, ARCHEOLOG, BADATEL, NEAKTIVNI_UZIVATEL}

    USER_ROLES = [
        (NEAKTIVNI_UZIVATEL_ID, NEAKTIVNI_UZIVATEL),
        (BADATEL_ID, BADATEL),
        (ARCHEOLOG_ID, ARCHEOLOG),
        (ARCHIVAR_ID, ARCHIVAR),
        (ADMIN_ID, ADMIN)
    ]

    USER_ROLES_DICT = {
        ADMIN: ADMIN_ID,
        ARCHEOLOG: ARCHEOLOG_ID,
        ARCHIVAR: ARCHIVAR_ID,
        BADATEL: BADATEL_ID,
        NEAKTIVNI_UZIVATEL: NEAKTIVNI_UZIVATEL_ID
    }

    # Permissions
    ADMIN3D = "Správce 3D"
    ACCOUNTS_ADMIN = "Příjem žádostí o aktivaci"
    USERS_ADMIN = "(De)aktivace uživatelů"

    ADMIN3D_ID = 1
    ACCOUNTS_ADMIN_ID = 2
    USERS_ADMIN_ID = 4

    USER_PERMISSIONS = [
        (ADMIN3D_ID, ADMIN3D),
        (ACCOUNTS_ADMIN_ID, ACCOUNTS_ADMIN),
        (USERS_ADMIN_ID, USERS_ADMIN)
    ]

    USER_PERMISSIONS_DICT = {
        ADMIN3D: ADMIN3D_ID,
        ACCOUNTS_ADMIN: ACCOUNTS_ADMIN_ID,
        USERS_ADMIN: USERS_ADMIN_ID
    }

    # Card header texts
    DET_CARD_HEADER = 'AMČR-PAS'
    DOC_CARD_HEADER = '3D'

    # Message types
    SUCCESS = 'success'
    ERROR = 'danger'

    # Message constants
    OBJECT_CREATED_SUCCESSFULLY = _('Záznam úspěšně vytvořen')
    OBJECT_DELETED_SUCCESSFULLY = _('Záznam úspěšně smazán')
    OBJECT_UPDATED_SUCCESSFULLY = _('Záznam byl aktualizován')
    OBEJCT_COULD_NOT_BE_CREATED = _('Chyba při vytváření záznamu')
    OBEJCT_COULD_NOT_BE_UPDATED = _('Chyba při aktualizaci záznamu')
    OBEJCT_COULD_NOT_BE_DELETED = _('Chyba při mazání záznamu')
    FILE_UPLOADED_SUCCESSFULLY = _('Soubor úspěšně připojen')
    FILE_COULD_NOT_BE_UPLOADED = _('Chyba při připojování souboru')
    FILE_COULD_NOT_BE_DOWNLOADED = _('Chyba při stahování souboru')
    NAME_ADDED_TO_THE_LIST = _('Jméno přidáno do hesláře')
    OBJECT_SENT_SUCCESSFULLY = _('Model úspěšně odeslán')
    OBJECT_ARCHIVED_SUCCESSFULLY = _('Model úspěšně archivován')
    OBJECT_RETURNED_TO_PREVIOUS_STATE = _('Model úspěšně vrácen')

    COOPERATION_REQUESTED = _("Žádost o spolupráci odeslána")
    COOPERATION_ACTIVATED = _("Spolupráce aktivována")
    COOPERATION_DEACTIVATED = _("Spolupráce deaktivována")
    COOPERATION_APPROVED = _("Spolupráce potvrzena")
    NAME_ALREADY_EXISTS = _("Jméno již existuje")
    LANGUAGE_CHANGED_MSG = _("Změna nastavení jayzka se projeví při dalším dotazu")
    FORM_IS_NOT_VALID = _("Forma není validní")

    # Heslare nazvy
    ACCESSIBILITY = 'pristupnost_selectable'
    AUTHOR = 'autor'
    CADASTRE = 'katastr'
    CADASTRE_1 = "katastry1"
    CADASTRE_2 = "katastry2"
    COORDINATE_SYSTEM = "souradnicovy_system"
    COUNTRY = 'zeme'
    DOCUMENT_STATE = 'stav_dokumentu'
    DOCUMENT_TYPE = "typ_dokumentu"
    EVENT_TYPE = 'typ_udalosti'
    FORMAT = 'format_dokumentu'
    REGION = 'kraj'
    REGIONS = "kraje"
    DISTRICTS = "okresy"
    ORGANIZATIONS = "organizace"
    PRESERVATION = "zachovalost"
    SERIES = "rada"
    STATE = 'stav'
    USERS = 'uzivatele'
    PREDMET_KIND2 = 'predmet_druh'
    PREDMET_KIND1 = 'predmet_kategorie'
    OBJECT_TYPE = 'typ_nalezu'
    OBJEKT_KIND2 = 'objekt_druh'
    OBJEKT_KIND1 = 'objekt_kategorie'
    OBJECT_SPECIFICATION = 'specifikace_predmetu'
    SPECIFICATION_FIRST = 'specifikace_objektu_prvni'
    SPECIFICATION_SECOND = 'specifikace_objektu_druha'
    PERIOD_FIRST = 'obdobi_prvni'
    PERIOD_SECOND = 'obdobi_druha'
    AREAL_FIRST = 'areal_prvni'
    AREAL_SECOND = 'areal_druha'
    CIRCUMSTANCE = 'nalezove_okolnosti'

    # Jine konstanty;
    DOCUMENT_ID = 'id_cj'
    EVENT_DESCRIPTION = 'popis_udalosti'
    USER = "uzivatel"
    YEAR_FROM = 'rok_od'
    YEAR_TO = 'rok_do'
    NOT_ENTERED_AUTHOR = 'Nezadán'

    # Create 3D document FORM additional constants
    DOC_AUTHORS_ORGANIZATION = "organizace_autora"
    DOC_YEAR_OF_CREATION = 'rok_vzniku'
    DOC_ORIGINAL_LABEL = 'oznaceni_originalu'
    DOC_DESCRIPTION = 'popis'
    DOC_NOTE = 'poznamka'
    DOC_FORMAT = 'format'
    DOC_LINK = 'odkaz'
    DOC_EASTING = 'easting'
    DOC_UTM = 'pas'
    DOC_NORTHING = 'northing'
    DOC_COUNTRY = 'zeme'
    DOC_REGION = 'region'
    DOC_CREDIBILITY = 'duveryhodnost'
    DOC_DESCRIPTION_DETAILS = 'popis_udalosti'

    # Heslaze obsah
    ACCESSIBILITY_CACHE = []
    DISTRICTS_CACHE = []
    DOCUMENT_TYPE_CACHE = []

    # States 3D documents
    DRAFT_STATE_ID = 1
    SENT_STATE_ID = 2
    ARCHIVED_STATE_ID = 3
    DRAFT_DOC = _('nerevidovaný')
    SENT_DOC = _('zapsaný')
    ARCHIVED_DOC = _('archivovaný')

    DOCUMENT_STATE_CACHE = [
        ('', '----'),
        (DRAFT_STATE_ID, DRAFT_DOC),
        (SENT_STATE_ID, SENT_DOC),
        (ARCHIVED_STATE_ID, ARCHIVED_DOC),
    ]
    DOCUMENT_STATE_DICT = {
        DRAFT_STATE_ID: DRAFT_DOC,
        SENT_STATE_ID: SENT_DOC,
        ARCHIVED_STATE_ID: ARCHIVED_DOC
    }

    # Typy prechodu stavu modelu 3D
    ZAPSANI = 1
    ODESLANI = 2
    ARCHIVACE = 3
    ZPET_K_ODESLANI = 4
    ZPET_K_ZAPSANI = 5
    AKTUALIZACE = 6
    ZMENA_AUTORA = 7

    TYPY_ZMENY_MODELU = [
        (ZAPSANI, _('Zápis')),  # 0 -> 1
        (ODESLANI, _('Odeslání')),  # 1 -> 2
        (ARCHIVACE, _('Archivace')),  # 2 -> 3
        (ZPET_K_ODESLANI, _('Vrácení k odeslání')),  # 3 -> 2
        (ZPET_K_ZAPSANI, _('Vrácení k zápisu')),  # 2 -> 1
        (AKTUALIZACE, _('Aktualizace')),
        (ZMENA_AUTORA, _('Změna autora'))
    ]

    CADASTRE_1_CACHE = []
    CADASTRE_2_CACHE = []
    CADASTRE_12_CACHE = []
    COORDINATE_SYSTEM_CACHE = [(1, 'WGS-84'), (2, 'S-JTSK')]
    EVENT_TYPE_CACHE = []
    ORGANIZATIONS_CACHE = []
    PRESERVATION_CACHE = []
    PERIOD_2_CACHE = []
    SERIES_CACHE = []
    REGIONS_CACHE = []
    USERS_CACHE = []
    NAMES_CACHE = []
    PROJECTS_CACHE = []
    PREDMET_KIND2_CACHE = []
    IDENTIFICATOR_CACHE = [
        ('', '----'),
        ('1', 'C'),
        ('2', 'M'),
    ]
    COUNTRIES_CACHE = []
    FORMAT_CACHE = []
    OBJECT_SPECIFICATION_CACHE = []
    OBJECT_TYPE_CACHE = []
    CIRCUMSTANCE_CACHE = []

    # Vicurovnove heslare
    PERIOD_12_CACHE = []  # obdobi_prvni + obdobi_druha
    AREAL_12_CACHE = []  # areal_prvni + areal_druha
    OBJEKT_KIND_12_CACHE = []  # objekt_druh + objekt_kategorie
    PREDMET_KIND_CACHE = []  # predmet_druh + predmet_kategorie
    SPECIFICATION_12_CACHE = []  # specifikace_objektu_prvni + specifikace_objektu_druha

    # Component activities

    AKTIVITA_SIDLISTNI = _('Sídlištní')
    AKTIVITA_POHREBNI = _('Pohřební')
    AKTIVITA_VYROBNI = _('Výrobní')
    AKTIVITA_TEZEBNI = _('Těžební')
    AKTIVITA_KULTOVNI = _('Kulturní')
    AKTIVITA_KOMUNIKACE = _('Komunikace')
    AKTIVITA_DEPONOVANI = _('Deponování')
    AKTIVITA_BOJ = _('Boj')
    AKTIVITA_JINA = _('Jiná')
    AKTIVITA_INTRUZE = _('Intruze')
    AKTIVITA_SIDLISTNI_ID = 1
    AKTIVITA_POHREBNI_ID = 2
    AKTIVITA_VYROBNI_ID = 3
    AKTIVITA_TEZEBNI_ID = 4
    AKTIVITA_KULTOVNI_ID = 5
    AKTIVITA_KOMUNIKACE_ID = 6
    AKTIVITA_DEPONOVANI_ID = 7
    AKTIVITA_BOJ_ID = 8
    AKTIVITA_JINA_ID = 9
    AKTIVITA_INTRUZE_ID = 10
    AKTIVITY_FIELDS = {
        AKTIVITA_SIDLISTNI_ID: 'aktivita_sidlistni',
        AKTIVITA_POHREBNI_ID: 'aktivita_pohrebni',
        AKTIVITA_VYROBNI_ID: 'aktivita_vyrobni',
        AKTIVITA_TEZEBNI_ID: 'aktivita_tezebni',
        AKTIVITA_KULTOVNI_ID: 'aktivita_kultovni',
        AKTIVITA_KOMUNIKACE_ID: 'aktivita_komunikace',
        AKTIVITA_DEPONOVANI_ID: 'aktivita_deponovani',
        AKTIVITA_BOJ_ID: 'aktivita_boj',
        AKTIVITA_JINA_ID: 'aktivita_jina',
        AKTIVITA_INTRUZE_ID: 'aktivita_intruze',
    }

    COMPONENT_ACTIVITIES = [
        (AKTIVITA_SIDLISTNI_ID, AKTIVITA_SIDLISTNI),
        (AKTIVITA_POHREBNI_ID, AKTIVITA_POHREBNI),
        (AKTIVITA_VYROBNI_ID, AKTIVITA_VYROBNI),
        (AKTIVITA_TEZEBNI_ID, AKTIVITA_TEZEBNI),
        (AKTIVITA_KULTOVNI_ID, AKTIVITA_KULTOVNI),
        (AKTIVITA_KOMUNIKACE_ID, AKTIVITA_KOMUNIKACE),
        (AKTIVITA_DEPONOVANI_ID, AKTIVITA_DEPONOVANI),
        (AKTIVITA_BOJ_ID, AKTIVITA_BOJ),
        (AKTIVITA_JINA_ID, AKTIVITA_JINA),
        (AKTIVITA_INTRUZE_ID, AKTIVITA_INTRUZE),
    ]

    # Heslare dictionaries
    ORGANIZATIONS_CACHE_DICT = {}
    AREAL_12_CACHE_DICT = {}
    PERIOD_12_CACHE_DICT = {}
    CADASTRY_DICT = {}

    # HTML constants GENERAL
    MAIN_MENU = _('Hlavní menu')
    HOME = _('Domů')
    CREATE = _('Zapsat')
    MY = _('Moje')
    CHOOSE = _('Vybrat')
    UPLOAD = _('Nahrát')

    #DOCUMENTS#
    LIBRARY_3D = _('Knihovna 3D')
    MODULE_3D = _('AMČR-PAS')
    MANAGE_DOC = _('Spravovat')

    #DETECTORS#
    MODUL_DETECTORS = _('Samostatné nálezy')
    COOP_DETECTOR = _('Spolupráce')
    CONFIRM_DETECTOR = _('Potvrdit')
    ARCHIVE_DETECTOR = _('Archivovat')
    SELECTED_FINDINGS = _('Vybrané nálezy')

    # USER
    USER_SETTINGS = _('Uživatelský účet')
