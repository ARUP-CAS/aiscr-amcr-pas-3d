from django.db import models
from detectors.models import Atree, HeslarPristupnost, UserStorage
from .constants import AmcrConstants as c


class HeslarRada(models.Model):
    nazev = models.TextField(blank=True, null=True)
    vysvetlivka = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_rada'


class HeslarTypDokumentu(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()
    klient = models.BooleanField()
    textove_data = models.BooleanField()
    obrazove_plany = models.BooleanField()
    letecke_foto = models.BooleanField()
    model = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heslar_typ_dokumentu'


class HeslarTypNalezu(models.Model):
    nazev = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_typ_nalezu'


class HeslarMaterialDokumentu(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()
    uplatneni = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heslar_material_dokumentu'


class HeslarJazykDokumentu(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_jazyk_dokumentu'


class HeslarUlozeniOriginalu(models.Model):
    poradi = models.SmallIntegerField()
    validated = models.SmallIntegerField()
    nazev = models.TextField()
    poznamka = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heslar_ulozeni_originalu'


class HeslarPismenoCj(models.Model):
    nazev = models.CharField(max_length=1)
    validated = models.SmallIntegerField()
    poradi = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_pismeno_cj'


class HeslarObdobiPrvni(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_obdobi_prvni'


class HeslarObdobiDruha(models.Model):
    prvni = models.ForeignKey(HeslarObdobiPrvni, models.DO_NOTHING, db_column='prvni', blank=True, null=True)
    nazev = models.TextField(blank=True, null=True)
    napoveda = models.TextField(blank=True, null=True)
    zkratka = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    rozsah_od = models.IntegerField(blank=True, null=True)
    rozsah_do = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()
    zahrnuje_take = models.TextField(blank=True, null=True)
    nadrazene = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heslar_obdobi_druha'


class HeslarArealPrvni(models.Model):
    nazev = models.TextField(blank=True, null=True)
    napoveda = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_areal_prvni'


class HeslarArealDruha(models.Model):
    prvni = models.ForeignKey(HeslarArealPrvni, models.DO_NOTHING, db_column='prvni', blank=True, null=True)
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    napoveda = models.TextField(blank=True, null=True)
    validated = models.SmallIntegerField()
    rozsah_do = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heslar_areal_druha'


class HeslarPredmetKategorie(models.Model):
    nazev = models.TextField()
    poradi = models.IntegerField()
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_predmet_kategorie'

    def __str__(self):
        return '{}'.format(self.nazev)


class HeslarPredmetDruh(models.Model):
    prvni = models.ForeignKey(HeslarPredmetKategorie, models.DO_NOTHING, db_column='prvni', blank=True, null=True)
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    implicitni_material = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_predmet_druh'


class HeslarObjektKategorie(models.Model):
    nazev = models.TextField()
    poradi = models.SmallIntegerField()
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_objekt_kategorie'


class HeslarObjektDruh(models.Model):
    prvni = models.ForeignKey(HeslarObjektKategorie, models.DO_NOTHING, db_column='prvni', blank=True, null=True)
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_objekt_druh'


class HeslarZeme(models.Model):
    nazev = models.TextField(blank=True, null=True)
    poradi = models.IntegerField(blank=True, null=True)
    validated = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'heslar_zeme'


class Dokument(models.Model):
    id = models.OneToOneField(Atree, models.DO_NOTHING, db_column='id', primary_key=True)
    rada = models.ForeignKey(HeslarRada, models.DO_NOTHING, db_column='rada')
    typ_dokumentu = models.ForeignKey(HeslarTypDokumentu, models.DO_NOTHING, db_column='typ_dokumentu')
    autor = models.TextField()
    organizace = models.IntegerField()
    rok_vzniku = models.IntegerField(blank=True, null=True)
    pristupnost = models.ForeignKey(HeslarPristupnost, models.DO_NOTHING, db_column='pristupnost', blank=True, null=True)
    material_originalu = models.ForeignKey(HeslarMaterialDokumentu, models.DO_NOTHING, db_column='material_originalu')
    jazyk_dokumentu = models.ForeignKey(HeslarJazykDokumentu, models.DO_NOTHING, db_column='jazyk_dokumentu')
    popis = models.TextField(blank=True, null=True)
    poznamka = models.TextField(blank=True, null=True)
    ulozeni_originalu = models.ForeignKey(HeslarUlozeniOriginalu, models.DO_NOTHING, db_column='ulozeni_originalu', blank=True, null=True)
    oznaceni_originalu = models.TextField(blank=True, null=True)
    odpovedny_pracovnik_vlozeni = models.ForeignKey(UserStorage, models.DO_NOTHING, db_column='odpovedny_pracovnik_vlozeni')
    datum_vlozeni = models.IntegerField()
    odpovedny_pracovnik_archivace = models.IntegerField()
    datum_archivace = models.IntegerField()
    stav = models.IntegerField()
    poradi = models.IntegerField()
    typ_dokumentu_posudek = models.TextField(blank=True, null=True)
    rok_vzniku_cj = models.IntegerField(blank=True, null=True)
    ident_cely = models.TextField(unique=True, blank=True, null=True)
    final_cj = models.BooleanField()
    letter_cj = models.ForeignKey(HeslarPismenoCj, models.DO_NOTHING, db_column='letter_cj', blank=True, null=True)
    datum_zverejneni = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dokument'


class ExtraData(models.Model):
    dokument = models.OneToOneField(Dokument, models.DO_NOTHING, db_column='dokument')
    datum_vzniku = models.DateTimeField(blank=True, null=True)
    pas = models.TextField(blank=True, null=True)
    easting = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=7)
    northing = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=7)
    zachovalost = models.IntegerField(blank=True, null=True)
    nahrada = models.IntegerField(blank=True, null=True)
    pocet_variant_originalu = models.IntegerField(blank=True, null=True)
    index = models.TextField(blank=True, null=True)
    odkaz = models.TextField(blank=True, null=True)
    format = models.IntegerField(blank=True, null=True)
    meritko = models.TextField(blank=True, null=True)
    vyska = models.IntegerField(blank=True, null=True)
    sirka = models.IntegerField(blank=True, null=True)
    cislo_objektu = models.TextField(blank=True, null=True)
    zeme = models.ForeignKey(HeslarZeme, on_delete=models.DO_NOTHING, db_column='zeme', blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    udalost = models.TextField(blank=True, null=True)
    udalost_typ = models.IntegerField(blank=True, null=True)
    rok_od = models.IntegerField(blank=True, null=True)
    rok_do = models.IntegerField(blank=True, null=True)
    osoby = models.TextField(blank=True, null=True)
    duveryhodnost = models.IntegerField(blank=True, null=True)
    geom = models.TextField(null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'extra_data'


class JednotkaDokument(models.Model):
    vazba = models.ForeignKey(Atree, models.DO_NOTHING, db_column='vazba', blank=True, null=True)
    poznamka = models.TextField(blank=True, null=True)
    dokument = models.ForeignKey(Dokument, models.DO_NOTHING, db_column='dokument')
    poradi = models.SmallIntegerField(blank=True, null=True)
    ident_cely = models.TextField(unique=True)
    vazba_druha = models.ForeignKey(Atree, models.DO_NOTHING, db_column='vazba_druha', related_name='jednotky_druhe', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jednotka_dokument'


class KomponentaDokument(models.Model):
    parent = models.ForeignKey(Atree, models.DO_NOTHING, db_column='parent', blank=True, null=True)
    obdobi = models.ForeignKey(HeslarObdobiDruha, models.DO_NOTHING, db_column='obdobi', blank=True, null=True)
    presna_datace = models.TextField(blank=True, null=True)
    areal = models.ForeignKey(HeslarArealDruha, models.DO_NOTHING, db_column='areal', blank=True, null=True)
    aktivita_sidlistni = models.BooleanField(blank=True, null=True)
    aktivita_pohrebni = models.BooleanField(blank=True, null=True)
    aktivita_vyrobni = models.BooleanField(blank=True, null=True)
    aktivita_tezebni = models.BooleanField(blank=True, null=True)
    aktivita_kultovni = models.BooleanField(blank=True, null=True)
    aktivita_komunikace = models.BooleanField(blank=True, null=True)
    aktivita_deponovani = models.BooleanField(blank=True, null=True)
    aktivita_boj = models.BooleanField(blank=True, null=True)
    aktivita_jina = models.BooleanField(blank=True, null=True)
    aktivita_intruze = models.BooleanField(blank=True, null=True)
    poznamka = models.TextField(blank=True, null=True)
    parent_poradi = models.IntegerField(blank=True, null=True)
    jistota = models.CharField(max_length=1, blank=True, null=True)
    jednotka_dokument = models.ForeignKey(JednotkaDokument, models.DO_NOTHING, db_column='jednotka_dokument', blank=True, null=True)
    ident_cely = models.TextField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'komponenta_dokument'


class NalezDokument(models.Model):
    komponenta_dokument = models.ForeignKey(KomponentaDokument, models.DO_NOTHING, db_column='komponenta_dokument')
    typ_nalezu = models.ForeignKey(HeslarTypNalezu, models.DO_NOTHING, db_column='typ_nalezu', blank=True, null=False)
    kategorie = models.IntegerField(blank=True, null=True)
    druh_nalezu = models.IntegerField(blank=True, null=True)
    specifikace = models.IntegerField(blank=True, null=True)
    pocet = models.TextField(blank=True, null=True)
    poznamka = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nalez_dokument'


class HistorieDokumentu(models.Model):
    datum_zmeny = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    typ_zmeny = models.IntegerField(default=0, choices=c.TYPY_ZMENY_MODELU, blank=False, null=False)
    dokument = models.ForeignKey(Dokument, on_delete=models.CASCADE, db_column='dokument', blank=False, null=False)
    uzivatel = models.ForeignKey(UserStorage, models.DO_NOTHING, db_column='uzivatel', blank=False, null=False)
    duvod = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'historie_dokumentu'
