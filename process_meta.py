# -*- coding: utf-8 -*-
import sys
import time
import datetime

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

import json

import profiles.models
import profiles.utilities
import profiles.search


def add_relation(person_1, person_2, rel_type, rel_note, recyprocal=None):
    if recyprocal == None:
        recyprocal = False
        
    if profiles.models.PersonRelation.objects.filter(source=person_1, target=person_2).count() == 0:
        rel1 = profiles.models.PersonRelation(source=person_1, target=person_2, type=rel_type, note=rel_note)
        rel1.save()
        print person_1.name, '=>', person_2.name, recyprocal
    
    if recyprocal:
        add_relation(person_2, person_1, rel_type, rel_note)


import types

def is_resource(value):
    return 'dbpedia.org/resource' in value

def splitter(values):
    resources = filter(is_resource, values)
    joined_names = filter(lambda x: not is_resource(x), values)
    simple_names = []
    map(lambda x: simple_names.extend(x.split(',')), joined_names)
    
    #names = map(lambda x: x.strip(), value.split(','))
    return resources + map(lambda x: x.strip(), simple_names)

def get_person_by_name(name, criteria=None):
    #print 'searching for', name
    if is_resource(name):
        return profiles.models.Person.objects.get(dbpedia_resource=name)
        
    candidates = profiles.search.perform_search(name)
    #print name
    print candidates
    return None


def process_relations(meta_key, direction, recyprocal=False):
    others = profiles.models.PersonMeta.objects.select_related().filter(meta_name=meta_key)
    #others = profiles.models.PersonMeta.objects.select_related().filter(person=profiles.models.Person.objects.get(name='Jorge Luis Borges')).filter(meta_name=meta_key)
    for other in others[0:100]:
        person = other.person
        #print person.name
        names = splitter(json.loads(other.meta_value))
        #print names
        
        for name in names:
            try:
                selected = get_person_by_name(name)
                if not selected:
                    continue
                    
                if direction == 'target':
                    add_relation(selected, person, meta_key, meta_key, recyprocal=recyprocal)
                else:
                    add_relation(person, selected, meta_key, meta_key, recyprocal=recyprocal)
            except Exception:
                pass
        
process_relations('influences', 'target', recyprocal=False)
process_relations('influenced', 'source', recyprocal=False)
