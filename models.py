from django.db import models

# base class for any resource from linked data
class Resource(models.Model):
    name = models.CharField(max_length=255, blank=False, db_index=True)
    uri = models.CharField(max_length=255, db_index=True, unique=True)

    class Meta:
        abstract = True
