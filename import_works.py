# -*- coding: utf-8 -*-
import sys
import time
import datetime

import json

try:
    import settings # Assumed to be in the same directory.
    #settings.DISABLE_TRANSACTION_MANAGEMENT = True
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

import django
import django.core.management
import django.core.exceptions
django.core.management.setup_environ(settings)

from django.db import transaction
import profiles.models
import profiles.importutils

import works.models


data_path = settings.DBPEDIA_DUMPS_DIR

ontology = data_path + '/instance_types_en.nt.bz2'
properties = data_path + '/mappingbased_properties_en.nt.bz2'
abstracts = data_path + '/short_abstracts_en.nt.bz2'
images = data_path + '/images_en.nt.bz2'
categories = data_path + '/article_categories_en.nt.bz2'
labels = data_path + '/labels_en.nt.bz2'
category_labels = data_path + '/category_labels_en.nt.bz2'

removable_types = set([
    'http://dbpedia.org/ontology/Work'
    , 'http://dbpedia.org/ontology/Film'
    , 'http://dbpedia.org/ontology/Book'
    , 'http://dbpedia.org/ontology/WrittenWork'
    , 'http://schema.org/CreativeWork'
])

def import_ontology(filename, max_count=None):
    if not max_count:
        max_count = -1
    
    i = 0
    for values in profiles.importutils.iter_entities_from(filename):
    
        #print i, person.dbpedia_resource
        #print values
        #types = set(values[u'22-rdf-syntax-ns#type'])
        #if not u'http://dbpedia.org/ontology/Work' in types: 
        #    continue

        if not 'author' in values:
            continue
            
        try:
            author = profiles.models.Person.objects.get(uri=values['author'][0])
        except profiles.models.Person.DoesNotExist:
            continue
            
        print author.name
        print values
        print ''
        
        if works.models.Work.objects.filter(uri=values['resource']).count() > 0:
            continue
        
        #continue
            
        
        work = author.work_set.create(uri=values['resource'])
        
        print author.name,'->', work.uri
        
        ##if rejected_types.intersection(types):
        #    continue
        
        #types = types.difference(removable_types)
        
        #person, created = profiles.models.Person.objects.get_or_create(uri=values['resource'])
    
        for (key, value) in values.iteritems():
            meta = works.models.WorkMeta(work=work, meta_name=key, meta_value=json.dumps(value))
            meta.save()
    
        i += 1
    
        #if created:
        #    meta = profiles.models.PersonMeta(person=person, meta_name='ontology_types', meta_value=json.dumps(list(types)))
        #    meta.save()
            #print values['resource'], 'saved', types
            
        #    if max_count > 0 and i == max_count:
        #        break
            
def import_titles(filename):
    
    i = 0
    for values in profiles.importutils.iter_entities_from(filename):            
        if not u'rdf-schema#label' in values:
            continue
          
        try:      
            work = profiles.models.Work.objects.get(uri=values['resource'])
        except profiles.models.Work.DoesNotExist:
            continue
            
        work.name = values[u'rdf-schema#label'][0]

        print work.name
        work.save()

        
        ##if rejected_types.intersection(types):
        #    continue
        
        #types = types.difference(removable_types)
        
        #person, created = profiles.models.Person.objects.get_or_create(uri=values['resource'])
    
        i += 1
    
        #if created:
        #    meta = profiles.models.PersonMeta(person=person, meta_name='ontology_types', meta_value=json.dumps(list(types)))
        #    meta.save()
            #print values['resource'], 'saved', types
            
        #    if max_count > 0 and i == max_count:
        #        break  

import_ontology(properties)
#import_titles(labels)
