from django.db import models

# base class for any resource from linked data
class Resource(models.Model):
    name = models.CharField(max_length=255, blank=False, db_index=True)
    uri = models.CharField(max_length=255, db_index=True, unique=True)
    wikipedia_url = models.CharField(max_length=255)
    original_depiction_url = models.CharField(max_length=255)
    depiction_url = models.CharField(max_length=255)
    thumbnail_url = models.CharField(max_length=255)
    pagerank_score = models.FloatField(default=0.0, db_index=True)
    authority_score = models.FloatField(default=0.0, db_index=True)
    hub_score = models.FloatField(default=0.0, db_index=True)

    class Meta:
        abstract = True
