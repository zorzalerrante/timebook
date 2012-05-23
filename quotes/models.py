from django.db import models

from profiles.models import Person
from works.models import Work
# Create your models here.

class Quote(models.Model):
    author = models.ForeignKey(Person, db_index=True)
    content = models.TextField()
    source_name = models.CharField(max_length=255)
    source = models.ForeignKey(Work, null=True)
    year = models.IntegerField(null=True)
    
    
