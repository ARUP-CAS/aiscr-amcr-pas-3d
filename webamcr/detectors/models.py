from django.db import models

from .constants import DetectorConstants as c
from django.conf import settings

class HeslarPristupnost(models.Model):
    nazev = models.CharField(max_length=1)
    vyznam = models.TextField()
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_pristupnost'


class HeslarTypOrganizace(models.Model):
    nazev = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()
    poradi = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_typ_organizace'


class Atree(models.Model):
    item_type = models.IntegerField(blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)
    ctime = models.DateTimeField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    caption = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atree'


class Organizace(models.Model):
    id = models.IntegerField(primary_key=True)
    nazev = models.TextField(blank=True, null=True)
    nazev_zkraceny = models.TextField(blank=True, null=True)
    zkratka = models.TextField(blank=True, null=True)
    typ_organizace = models.ForeignKey(HeslarTypOrganizace, models.DO_NOTHING, db_column='typ_organizace', blank=True, null=True)
    oao = models.BooleanField(blank=True, null=True)
    published_accessibility = models.ForeignKey(HeslarPristupnost, models.DO_NOTHING, db_column='published_accessibility')
    months_to_publication = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'organizace'


class UserStorage(models.Model):
    id = models.OneToOneField(Atree, models.DO_NOTHING, db_column='id', primary_key=True)
    jmeno = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    pasw = models.TextField(blank=True, null=True)
    auth_level = models.IntegerField(blank=True, null=True)
    telefon = models.TextField(blank=True, null=True)
    # ID je stejne jako PK v tabulce Organizace proto zde odpojuji relaci na Atree
    organizace = models.ForeignKey(Organizace, models.DO_NOTHING, related_name='user_organizace', db_column='organizace', blank=True, null=True)
    news = models.IntegerField(blank=True, null=True)
    prijmeni = models.TextField(blank=True, null=True)
    confirmation = models.TextField(blank=True, null=True)
    notifikace_nalezu = models.BooleanField()
    ident_cely = models.TextField()
    jazyk = models.CharField(max_length=15, choices=settings.LANGUAGES, null=False, default='cs')

    class Meta:
        managed = False
        db_table = 'user_storage'


class VazbaSpoluprace(models.Model):
    badatel = models.ForeignKey(UserStorage, on_delete=models.DO_NOTHING, related_name='spoluprace_badatele', db_column='badatel', blank=True, null=True)
    archeolog = models.ForeignKey(UserStorage, on_delete=models.DO_NOTHING, related_name='spoluprace_archeologove', db_column='archeolog', blank=True, null=True)
    aktivni = models.BooleanField(blank=True, null=True)
    potvrzeno = models.BooleanField(blank=True, null=True)
    datum_vytvoreni = models.IntegerField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'vazba_spoluprace'


class SamostatnyNalez(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    inv_cislo = models.TextField(null=True)
    projekt = models.IntegerField(null=True)
    katastr = models.IntegerField(null=True)
    lokalizace = models.TextField(null=True)
    okolnosti = models.IntegerField(null=True)
    geom = models.TextField(null=True)  # This field type is a guess. There should be a GeometryField of the GeoDjango library https://docs.djangoproject.com/en/2.2/ref/contrib/gis/install/#windows
    pristupnost = models.IntegerField(null=True)
    obdobi = models.IntegerField(null=True)
    presna_datace = models.TextField(null=True)
    typ_nalezu = models.IntegerField(null=True)
    druh_nalezu = models.IntegerField(null=True)
    specifikace = models.IntegerField(null=True)
    pocet = models.IntegerField(null=True)
    poznamka = models.TextField(null=True)
    nalezce = models.ForeignKey(UserStorage, models.DO_NOTHING, db_column='nalezce',null=True)
    datum_nalezu = models.DateField(null=True)
    odpovedny_pracovnik_vlozeni = models.IntegerField(null=True)
    datum_vlozeni = models.IntegerField(null=True)
    odpovedny_pracovnik_archivace = models.IntegerField(null=True)
    datum_archivace = models.IntegerField(null=True)
    stav = models.IntegerField(null=False)
    predano = models.BooleanField(null=True)
    predano_organizace = models.IntegerField(null=True)
    poradi = models.IntegerField(null=True)
    ident_cely = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'samostatny_nalez'


class Soubor(models.Model):
    dokument = models.IntegerField(blank=True, null=True)
    nazev = models.TextField()
    uzivatelske_oznaceni = models.TextField(blank=True, null=True)
    rozsah = models.IntegerField(blank=True, null=True)
    vlastnik = models.IntegerField()
    filepath = models.TextField(unique=True)
    mimetype = models.TextField()
    size_bytes = models.IntegerField()
    nahled = models.IntegerField(blank=True, null=True)
    vytvoreno = models.DateField(blank=True, null=True)
    projekt = models.IntegerField(blank=True, null=True)
    typ_souboru = models.TextField(blank=True, null=True)
    samostatny_nalez = models.ForeignKey(SamostatnyNalez, models.DO_NOTHING, db_column='samostatny_nalez', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'soubor'


class HistorieSpoluprace(models.Model):
    datum_zmeny = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    typ_zmeny = models.IntegerField(default=0, choices=c.TYP_ZMENY_SPOLUPRACE, blank=False, null=False)
    vazba_spoluprace = models.ForeignKey(VazbaSpoluprace, on_delete=models.CASCADE, db_column='vazba_spoluprace', blank=False, null=False)
    uzivatel = models.ForeignKey(UserStorage, models.DO_NOTHING, db_column='uzivatel', blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'historie_spoluprace'


class HistorieSamNalezu(models.Model):
    datum_zmeny = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    typ_zmeny = models.IntegerField(default=0, choices=c.TYPY_ZMENY_SAM_NALEZU, blank=False, null=False)
    samostatny_nalez = models.ForeignKey(SamostatnyNalez, on_delete=models.CASCADE, db_column='samostatny_nalez', blank=False, null=False)
    uzivatel = models.ForeignKey(UserStorage, models.DO_NOTHING, db_column='uzivatel', blank=False, null=False)
    duvod = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'historie_samostatny_nalez'

# ------------------ MODELY PRO PROJEKT ----------------------

class HeslarJmena(models.Model):
    jmeno = models.TextField(blank=True, null=True)
    prijmeni = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()
    vypis = models.TextField(blank=True, null=True)
    vypis_cely = models.TextField(unique=True, blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'heslar_jmena'
        unique_together = (('jmeno', 'prijmeni'),)


class HeslarKulturniPamatka(models.Model):
    nazev = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()
    poradi = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_kulturni_pamatka'


class HeslarTypProjektu(models.Model):
    nazev = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()
    poradi = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_typ_projektu'


class Projekt(models.Model):
    id = models.OneToOneField(Atree, models.DO_NOTHING, db_column='id', primary_key=True)
    odpovedny_pracovnik_zapisu = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_zapisu', db_column='odpovedny_pracovnik_zapisu', blank=True, null=True)
    odpovedny_pracovnik_prihlaseni = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_prihlaseni', db_column='odpovedny_pracovnik_prihlaseni', blank=True, null=True)
    odpovedny_pracovnik_archivace = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_archivace', db_column='odpovedny_pracovnik_archivace', blank=True, null=True)
    stav = models.SmallIntegerField(blank=True, null=True)
    time_of_change = models.IntegerField(blank=True, null=True)
    odpovedny_pracovnik_navrhu_zruseni = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_navrhu_zruseni', db_column='odpovedny_pracovnik_navrhu_zruseni', blank=True, null=True)
    odpovedny_pracovnik_zruseni = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_zruseni', db_column='odpovedny_pracovnik_zruseni', blank=True, null=True)
    adresa = models.TextField(blank=True, null=True)
    dalsi_katastry = models.TextField(blank=True, null=True)
    typ_projektu = models.ForeignKey(HeslarTypProjektu, related_name='projekty_typy', on_delete=models.DO_NOTHING, db_column='typ_projektu', blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    katastr = models.ForeignKey(Atree, on_delete=models.DO_NOTHING, related_name='katasters', db_column='katastr', blank=True, null=True)
    lokalita = models.TextField(blank=True, null=True)
    nkp_cislo = models.TextField(blank=True, null=True)
    nkp_popis = models.TextField(blank=True, null=True)
    objednatel = models.TextField(blank=True, null=True)
    odpovedna_osoba = models.TextField(blank=True, null=True)
    parcelni_cislo = models.TextField(blank=True, null=True)
    podnet = models.TextField(blank=True, null=True)
    okres = models.ForeignKey(Atree, on_delete=models.DO_NOTHING, related_name='okresy', db_column='okres', blank=True, null=True)
    telefon = models.TextField(blank=True, null=True)
    uzivatelske_oznaceni = models.TextField(blank=True, null=True)
    vedouci_projektu = models.ForeignKey(HeslarJmena, on_delete=models.DO_NOTHING, related_name='projekty_vedouci', db_column='vedouci_projektu', blank=True, null=True)
    datum_zapisu = models.DateField(blank=True, null=True)
    datum_prihlaseni = models.DateField(blank=True, null=True)
    datum_zahajeni = models.DateField(blank=True, null=True)
    datum_ukonceni = models.DateField(blank=True, null=True)
    datum_archivace = models.DateField(blank=True, null=True)
    datum_navrzeni_zruseni = models.DateField(blank=True, null=True)
    datum_zruseni = models.DateField(blank=True, null=True)
    duvod_navrzeni_zruseni = models.TextField(blank=True, null=True)
    datum_navrhu_archivace = models.DateField(blank=True, null=True)
    odpovedny_pracovnik_navrhu_archivace = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, db_column='odpovedny_pracovnik_navrhu_archivace', blank=True, null=True)
    id_rok = models.IntegerField(blank=True, null=True)
    id_poradi = models.IntegerField(blank=True, null=True)
    planovane_zahajeni = models.TextField(blank=True, null=True)
    kulturni_pamatka = models.ForeignKey(HeslarKulturniPamatka, on_delete=models.DO_NOTHING, db_column='kulturni_pamatka', blank=True, null=True)
    datum_zapisu_zahajeni = models.DateField(blank=True, null=True)
    odpovedny_pracovnik_zahajeni = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_zahajeni', db_column='odpovedny_pracovnik_zahajeni', blank=True, null=True)
    datum_zapisu_ukonceni = models.DateField(blank=True, null=True)
    odpovedny_pracovnik_ukonceni = models.ForeignKey('UserStorage', on_delete=models.DO_NOTHING, related_name='odpovedny_pracovnici_ukonceni', db_column='odpovedny_pracovnik_ukonceni', blank=True, null=True)
    termin_odevzdani_nz = models.DateField(blank=True, null=True)
    ident_cely = models.TextField(unique=True, blank=True, null=True)
    datetime_born = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'projekt'


class UserGroupAuthStorage(models.Model):
    id = models.OneToOneField(Atree, models.DO_NOTHING, db_column='id', primary_key=True)
    user_group = models.ForeignKey(Atree, models.DO_NOTHING, related_name='auth_storages', blank=True, null=True)
    auth_level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_group_auth_storage'


class HeslarNalezoveOkolnosti(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField()
    vysvetlivka = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
