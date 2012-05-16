from django.db import models
import timebook.models
import profiles.models

class Genre(timebook.models.Resource):
    pass 
    
class Work(timebook.models.Resource):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(db_index=True, null=True)
    genres = models.ManyToManyField(Genre, db_index=True)
    authors = models.ManyToManyField(profiles.models.Person, db_index=True)
    
class WorkMeta(models.Model):
    work = models.ForeignKey(Work, db_index=True)
    meta_name = models.CharField(max_length=255, db_index=True)
    meta_value = models.TextField()
