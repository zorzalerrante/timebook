from django.db import models
import dbpedia.models


class Category(dbpedia.models.Resource):
    count = models.IntegerField(default=0)
    avg_score = models.IntegerField(default=0, db_index=True)
    min_year = models.IntegerField(null=True, db_index=True)
    max_year = models.IntegerField(null=True, db_index=True)
    
class Person(dbpedia.models.Resource):
    birth_year = models.IntegerField(db_index=True, null=True)
    death_year = models.IntegerField(db_index=True, null=True)
    is_relevant = models.BooleanField(default=False, db_index=True)
    groups = models.ManyToManyField(Category, db_index=True)
    relations = models.ManyToManyField('self', db_index=True, symmetrical=False, through='Relation')
    score = models.IntegerField(default=0, db_index=True)
        
class PersonMeta(models.Model):
    person = models.ForeignKey(Person, db_index=True)
    meta_name = models.CharField(max_length=255, db_index=True)
    meta_value = models.TextField()

class Relation(models.Model):    
    source = models.ForeignKey(Person, db_index=True, related_name='source')
    target = models.ForeignKey(Person, db_index=True, related_name='target')
    origin = models.CharField(max_length=255, db_index=True)


