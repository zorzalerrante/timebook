# -*- coding: utf-8 -*-
import settings
import django
import django.core.management
import django.core.exceptions
import re
django.core.management.setup_environ(settings)


import datetime
import json

from django.db import transaction
import profiles.models
import profiles.importutils

# our source files
#data_path = 'dbpedia'
data_path = settings.DBPEDIA_DUMPS_DIR

ontology = data_path + '/instance_types_en.nt.bz2'
properties = data_path + '/mappingbased_properties_en.nt.bz2'
abstracts = data_path + '/short_abstracts_en.nt.bz2'
images = data_path + '/images_en.nt.bz2'
categories = data_path + '/article_categories_en.nt.bz2'
labels = data_path + '/labels_en.nt.bz2'
category_labels = data_path + '/category_labels_en.nt.bz2'

# some names are in the form Last Name, First Name.
def remove_colons(name):
    name = map(lambda x: x.strip(), name.split(','))
    if len(name) > 2:
        name[0], name[1] = name[1], name[0]
    else:
        name.reverse()
    return ' '.join(name)
    
    
def relation_exists(person1, person2):
    return profiles.models.Relation.objects.filter(source=person1, target=person2).count() > 0

# TODO: we're not using this...
ignored_meta = (
    'resource', 'wikiPageUsesTemplate', 'alternativeNames'
)    

# TODO: we're not using this... 
relevant_types = set([
    'http://dbpedia.org/ontology/Artist' 
    , 'http://dbpedia.org/ontology/Scientist'
    , 'http://dbpedia.org/ontology/Writer'
    , 'http://dbpedia.org/ontology/Philosopher'
    , 'http://dbpedia.org/ontology/Journalist'
    , 'http://dbpedia.org/ontology/Politician'    
])


def import_ontology(filename, max_count=None):
    if not max_count:
        max_count = -1
    
    i = 0
    
    removable_types = set([
        'http://dbpedia.org/ontology/Person'
        , 'http://www.w3.org/2002/07/owl#Thing'
        , 'http://xmlns.com/foaf/0.1/Person'
        , 'http://schema.org/Person'
    ])
    
    rejected_types = set([
        'http://dbpedia.org/ontology/FictionalCharacter'
        , 'http://dbpedia.org/ontology/PersonFunction'
    ])
    
    for values in profiles.importutils.iter_entities_from(filename):
    
        #print i, person.dbpedia_resource
        #print values
        types = set(values[u'22-rdf-syntax-ns#type'])
        if not u'http://dbpedia.org/ontology/Person' in types: 
            continue
        
        if rejected_types.intersection(types):
            continue
        
        types = types.difference(removable_types)
        
        person, created = profiles.models.Person.objects.get_or_create(uri=values['resource'])
    
        i += 1
    
        if created:
            meta = profiles.models.PersonMeta(person=person, meta_name='ontology_types', meta_value=json.dumps(list(types)))
            meta.save()
            #print values['resource'], 'saved', types
            
            if max_count > 0 and i == max_count:
                break



def import_properties(filename):
    i = 0
    
    total_persons = profiles.models.Person.objects.all().count()
    if total_persons == 0:
        return
        
    for values in profiles.importutils.iter_entities_from(filename):
        # primero vemos si la persona esta
        try:
            person = profiles.models.Person.objects.get(uri=values['resource'])
        except profiles.models.Person.DoesNotExist:
            #print values['resource'], 'not a recognized person'
            continue
            
        if profiles.models.PersonMeta.objects.filter(person=person).count() > 1:
            i += 1
            
            if i == total_persons:
                break
            continue
            
        i += 1
        del values['resource']
        #print values.keys()
        
        for (key, value) in values.iteritems():
            meta = profiles.models.PersonMeta(person=person, meta_name=key, meta_value=json.dumps(value))
            meta.save()
        
        if i == total_persons:
            break



def define_relevants():
    relevant_dbpedia_fields = (
        'movement', 'schoolTradition', 'philosophicalSchool'
        , 'genre', 'notableWorks', 'notableIdeas', 'notableStudent'
        , 'influenced', 'influences', 'influencedBy'
        , 'academicAdvisor', 'doctoralAdvisor', 'doctoralStudents', 'almaMater'
        , 'party'
    )
    
    #candidates = profiles.models.PersonMeta.objects.select_related().filter(meta_name__in=relevant_dbpedia_fields).filter(person__is_relevant=False)
    candidates = profiles.models.Person.objects.filter(personmeta__meta_name__in=relevant_dbpedia_fields).filter(is_relevant=False).distinct()
    print "total candidates:", candidates.count()
    
    for p in candidates:
        #print pm.person.dbpedia_resource, 'relevant'
        p.is_relevant = True
        p.save()

    connection_fields = (
        'notableStudent', 'influenced', 'influences', 'influencedBy'
        , 'academicAdvisor', 'doctoralAdvisor', 'doctoralStudents'
    )
    
    find_new = True
    
    while find_new:
        # buscamos los que si son relevantes y que tienen estos campos
        sources = profiles.models.Person.objects.filter(personmeta__meta_name__in=connection_fields).filter(is_relevant=True).distinct()
        print "total interesting relevants:", sources.count()
        
        new_relevants = set()
        
        for i in xrange(0, sources.count(), 10000):
            for p in sources[i:i+10000]:
                meta = p.personmeta_set.filter(meta_name__in=relevant_dbpedia_fields)
                
                for m in meta:
                    candidate_resources = json.loads(m.meta_value)                 
                    new_candidates = profiles.models.Person.objects.filter(uri__in=candidate_resources).filter(is_relevant=False)
            
                    for c in new_candidates:
                        new_relevants.add(c.id)
                        
        if not new_relevants:
            find_new = False
            print 'no more relevants found'
        else:
            profiles.models.Person.objects.filter(id__in=list(new_relevants)).update(is_relevant=True)
            print 'added', len(new_relevants), 'new relevants. looking for more'
    
    
    
def import_categories(filename):
    banned_names = ( '_births', '_deaths', 'Living_people', 'Deaths_from_', 'People_from_', '_crimes', 'Protected_redirects')
    
    def test_categories(person, values):
        subjects = values['subject']
        for b in banned_names:
            subjects = filter(lambda x: b not in x, subjects)
            
        categories = map(lambda x: profiles.models.Category.objects.get_or_create(uri=x)[0], subjects)
            
        person.groups = categories
        
        print person.uri
        for c in categories: print '--', c.uri
        
    profiles.importutils.iter_on_relevant_entities(filename, test_categories)
    
     
                

    
    
def build_relations():
    relevant_dbpedia_fields = {
        'notableStudent': 'target', 
        'influenced': 'target', 
        'influences': 'target', 
        'influencedBy': 'source', 
        'academicAdvisor': 'source', 
        'doctoralAdvisor': 'source', 
        'doctoralStudents': 'target'
    }
    
    sources = profiles.models.Person.objects.filter(personmeta__meta_name__in=relevant_dbpedia_fields).filter(is_relevant=True).distinct()
    
    for p in sources:
        print p.uri
        meta = p.personmeta_set.filter(meta_name__in=relevant_dbpedia_fields.keys())
        
        for m in meta:
            candidate_resources = json.loads(m.meta_value)                 
            candidates = profiles.models.Person.objects.filter(uri__in=candidate_resources).filter(is_relevant=True)
            
            for c in candidates:
                rel = None
                if relevant_dbpedia_fields[m.meta_name] == 'source':
                    print '-->', c.uri
                    if not relation_exists(p, c):
                        rel = profiles.models.Relation(source=p, target=c, origin=m.meta_name)
                else:
                    print '<--', c.uri
                    if not relation_exists(c, p):
                        rel = profiles.models.Relation(source=c, target=p, origin=m.meta_name)
                    
                if rel != None:
                    rel.save()
                else:
                    print 'already exists'



def build_profiles():
    dateRegexp = re.compile('(-?[0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])')
    sources = profiles.models.Person.objects.filter(is_relevant=True)
    
    for p in sources:
        meta = p.personmeta_set.all()
        
        for m in meta:
            values = json.loads(m.meta_value)
            
            
            if m.meta_name == 'name':
                p.name = values[0].strip()
            if m.meta_name == 'birthDate':
                match = dateRegexp.match(values[0].strip())
                p.birth_year = int(match.group(1))
            if m.meta_name == 'birthYear':
                p.birth_year = int(values[0].strip())
            if m.meta_name == 'deathDate':
                match = dateRegexp.match(values[0].strip())
                p.death_year = int(match.group(1))
            if m.meta_name == 'deathYear':
                p.death_year = int(values[0].strip())
            #if p.name or p.birth_year or p.death_year:
        p.save()
        print p.name
            
            
            
def build_labels(filename):
    def test_label(person, values):
        person.name = values[u'rdf-schema#label'][0]
        person.save()
        print person.uri, person.name
        
    profiles.importutils.iter_on_relevant_entities(filename, test_label)



def build_category_labels(filename):
    i = 0
    total_categories = profiles.models.Category.objects.all().count()
    if total_categories == 0:
        return
        
    for values in profiles.importutils.iter_entities_from(filename):
        try:
            category = profiles.models.Category.objects.get(uri=values['resource'])
        except profiles.models.Category.DoesNotExist:
            continue
            
        i += 1

        category.name = values[u'rdf-schema#label'][0]
        category.save()
        
        print category.uri, ':', category.name
       
        if i == total_categories:
            break


def build_abstracts(filename):
    def test_abstract(person, values):
        abstract = values[u'rdf-schema#comment'][0]
        meta = profiles.models.PersonMeta(person=person, meta_name='abstract', meta_value=json.dumps(abstract))
        meta.save()
        print person.name, abstract
        
    profiles.importutils.iter_on_relevant_entities(filename, test_abstract)
    
    
    
def build_images(filename):
    def test_images(person, values):
        try:
            print person.uri, values['depiction'][0]
            person.depiction = values['depiction'][0]
            person.save()
        except Exception as e:
            print str(e)
        
    profiles.importutils.iter_on_relevant_entities(filename, test_images)



if __name__ == '__main__':
    print 'ontology...'
    #import_ontology(ontology, max_count=None)
    print 'done'

    print 'properties...'
    #import_properties(properties)
    print 'done'

    print 'relevants...'
    #define_relevants()
    print 'done...'
     
    print 'categories...'
    #import_categories(categories)
    print 'done'

    print 'relations...'
    #build_relations()
    print 'done'


    print 'labels....'
    #build_labels(labels)
    #build_category_labels(category_labels)
    print 'done'

    print 'profiles...'
    #build_profiles()
    print 'done'

    print 'abstracts....'
    #build_abstracts(abstracts)
    print 'done'

    print 'images...'
    build_images(images)
    print 'done'

