from django.db import models
from detectors.models import UserStorage
from detectors.constants import DetectorConstants as c


class HistorieUserStorage(models.Model):
    datum_zmeny = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    typ_zmeny = models.IntegerField(default=0, choices=c.TYPY_ZMENY_USER_STORAGE, blank=False, null=False)
    ucet = models.ForeignKey(UserStorage, on_delete=models.CASCADE, related_name='historie_meho_uctu', blank=False, null=False)
    uzivatel = models.ForeignKey(UserStorage, on_delete=models.DO_NOTHING, related_name='zmeny_jinych_uctu', blank=False, null=False)
    komentar = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'historie_user_storage'
