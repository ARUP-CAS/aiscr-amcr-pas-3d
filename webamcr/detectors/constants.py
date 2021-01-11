from django.utils.translation import gettext_lazy as _
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectorConstants:
    # Typy prechodu stavu spoluprace
    SPOLUPRACE_ZADOST = 1
    SPOLUPRACE_AKTIVACE = 2
    SPOLUPRACE_DEAKTIVACE = 3
    SPOLUPRACE_POTVRZENI = 4

    TYP_ZMENY_SPOLUPRACE = [
        (SPOLUPRACE_ZADOST, _('Žádost')),
        (SPOLUPRACE_AKTIVACE, _('Aktivace')),
        (SPOLUPRACE_DEAKTIVACE, _('Deaktivace')),
        (SPOLUPRACE_POTVRZENI, _('Potvrzení')),
    ]

    # Typy prechodu stavu samostatnych nalezu
    ZAPSANI = 1
    ODESLANI = 2
    POTVRZENI = 3
    ARCHIVACE = 4
    ZPET_K_ARCHIVACI = 5
    ZPET_K_POTVRZENI = 6
    ZPET_K_ODESLANI = 7
    AKTUALIZACE = 8

    TYPY_ZMENY_SAM_NALEZU = [
        (ZAPSANI, _('Zápis')),  # 0 -> 1
        (ODESLANI, _('Odeslání')),  # 1 -> 2
        (POTVRZENI, _('Potvrzení')),  # 2 -> 3
        (ARCHIVACE, _('Archivace')),  # 3 -> 4
        (ZPET_K_ARCHIVACI, _('Vrácení k archivaci')),  # 4 -> 3
        (ZPET_K_POTVRZENI, _('Vrácení k potvrzení')),  # 3 -> 2
        (ZPET_K_ODESLANI, _('Vrácení k odeslání')),  # 2 -> 1
        (AKTUALIZACE, _('Aktualizace')),
    ]

    # Stavy samostatnych nalezu
    ZAPSANY = 1
    ODESLANY = 2
    POTVRZENY = 3
    ARCHIVOVANY = 4

    DETECTOR_STATE_CACHE = [
        (ZAPSANY, _('zapsaný')),
        (ODESLANY, _('odeslaný')),  # Odeslaný
        (POTVRZENY, _('potvrzený')),  # Potvrzeny
        (ARCHIVOVANY, _('archivovaný')),
    ]

    UNKNOWN = 'Neznámý'

    # Zmeny uzivatelu

    VYTVORENI = 1
    EDITACE = 2
    ZMENA_ROLE = 3

    TYPY_ZMENY_USER_STORAGE = [
        (VYTVORENI, _('Vytvoření uživatele')),
        (EDITACE, _('Editace uživatele')),
        (ZMENA_ROLE, _('Změna role')),
    ]

    # Stavy projektu
    PROJEKT_STAV_OZNAMENY = 0
    PROJEKT_STAV_REGISTROVANY = 1
    PROJEKT_STAV_PRIHLASENY = 2
    PROJEKT_STAV_ZAHAJENY = 3
    PROJEKT_STAV_UKONCENY = 4
    PROJEKT_STAV_NAVRZEN_K_ARCHIVACI = 5
    PROJEKT_STAV_ARCHIVOVANY = 6
    PROJEKT_STAV_NAVRZEN_KE_ZRUSENI = 7
    PROJEKT_STAV_ZRUSENY = 8

