from django.db import models
import timebook.models


class Category(timebook.models.Resource):
    count = models.IntegerField(default=0)
     
class Person(timebook.models.Resource):
    birth_year = models.IntegerField(db_index=True, null=True)
    death_year = models.IntegerField(db_index=True, null=True)
    is_relevant = models.BooleanField(default=False, db_index=True)
    depiction = models.CharField(max_length=255)
    wikipedia_url = models.CharField(max_length=255)
    pagerank = models.FloatField(default=0.0)
    groups = models.ManyToManyField(Category, db_index=True)
    relations = models.ManyToManyField('self', db_index=True, symmetrical=False, through='Relation') 
    
class PersonMeta(models.Model):
    person = models.ForeignKey(Person, db_index=True)
    meta_name = models.CharField(max_length=255, db_index=True)
    meta_value = models.TextField()

class Relation(models.Model):    
    source = models.ForeignKey(Person, db_index=True, related_name='source')
    target = models.ForeignKey(Person, db_index=True, related_name='target')
    origin = models.CharField(max_length=255, db_index=True)

