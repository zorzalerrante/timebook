import re
from urllib import unquote
import datetime
import json
import bz2

import models

# returns true if the values represent a person

person_fields = (
    'birthYear', 'deathYear', 'birthPlace', 'birthDate', 'deathPlace', 'deathDate'
    , 'placeOfDeath', 'dateOfDeath', 'placeOfBirth', 'dateOfBirth'
    , 'spouse', 'children', 'child'
    , 'training', 'field'
    , 'movement', 'schoolTradition', 'philosophicalSchool'
    , 'genre', 'notableWorks', 'notableworks', 'notableIdeas', 'notableStudent'
    , 'influenced', 'influences', 'influencedBy'
    , 'academicAdvisor', 'doctoralAdvisor', 'doctoralStudents'
)

person_banned_names = (
    'list_of', 'career_', '_election', 'positions_', 'presidency_of', 'influence'
)

def is_person(values):
    resource = values['resource'].lower()
    for b in person_banned_names:
        if b in resource:
            return False
            
    for f in person_fields:
        if f in values:
            return True
            
    return False
    
checked_fields = (
    'birthdate', 'dateOfBirth'
)
    
# returns true if the person seems to be already on the index. this happens because some entities are repeated in dbpedia data
# example: William Shakespeare appears twice
# http://dbpedia.org/resource/William_Shakespeare
# http://dbpedia.org/resource/Shakespeare%27s_influence
def maybe_person_exists(values):
    # easy: check if we have already this resource.
    if models.Person.objects.filter(dbpedia_resource=values['resource']).count() > 0:
        return True
        
    # since the resource is not there, let's check the name.
    name = values['name'][0]
    
    # some duplicates encode the resource in the name. weird, but it happens (ex.: see one of the duplicates of Obama)
    resources = filter(lambda x: 'dbpedia.org/resource' in x, values['name'])
    if resources:
        if models.Person.objects.filter(dbpedia_resource__in=resources).count() > 0:
            return True
    
    named = models.Person.objects.filter(name__in=values['name'])

    if named.count() > 0:
        dates = set()
        for f in checked_fields:
            if f in values:
                dates.update(values[f])
        
        if dates:
            # no sense to check if we don't have the dates
            for p in named:
                meta = models.PersonMeta.objects.filter(person=p, meta_name__in=checked_fields)
                candidates = set()
                for m in meta:
                    value = json.loads(m.meta_value)
                    candidates.update(value)
                    
                if dates.intersection(candidates):
                    return True
    
    return False
    
# returns true if we should save this person? in the databse

occupation_fields = ('occupation', 'area', 'shortDescription', 'profession')

relevant_occupations = (
    'writer', 'artist', 'poet'
    , 'painter'
    , 'director', 'illustrator', 'graphic novelist', 'cartoonist'
    , 'cinematographer', 'composer', 'singer', 'journalist', 'novelist', 'historian', 'essayist', 'author'
    , 'dramatist'
    , 'inventor', 'scientist', 'physician', 'mathematician', 'engineer'
)

relevant_dbpedia_fields = (
    'movement', 'schoolTradition', 'philosophicalSchool'
    , 'genre', 'notableWorks', 'notableworks', 'notableIdeas', 'notableStudent'
    , 'influenced', 'influences', 'influencedBy'
    , 'academicAdvisor', 'doctoralAdvisor', 'doctoralStudents', 'almaMater'
    , 'party'
)

banned_fields = (
    'category'
)

# check out that sometimes they have a genre
def is_interesting(values):
    #name = get_best_name(values['name'])
    #if not 'Shakespeare' in name:
    #    return False
    
    for f in relevant_dbpedia_fields:
        #value = get_attr(values, f, default='').encode('utf-8', errors='ignore')
        if f in values:
            return True
            
    for f in banned_fields:
        if f in values:
            return False
    
    for f in occupation_fields:
        if f in values:
            for occupation in values[f]:
                test = occupation.encode('utf-8', errors='ignore').lower()
    
                if test:
                    for occ in relevant_occupations:
                        if occ in test:
                            return True

    #print 'not interesting!'
    #print values
    return False

# bz2 wikipedia n-triples import
def iter_entities_from(filename):
    with bz2.BZ2File(filename, 'r') as dump:
        prev_resource = None
        values = None

        for l in dump:
            parts = get_parts(l)
            resource = parts['resource']

            if prev_resource != resource:
                if prev_resource != None:
                    yield values

                values = {'resource': resource}
                prev_resource = resource


            value = parts['object']
            if not value: 
                continue

            key = parts['predicate']

            if not key in values:
                values[key] = [value]
            else:
                values[key].append(value)

        yield values
    
def iter_on_relevant_entities(filename, func):
    i = 0
    
    total_persons = models.Person.objects.filter(is_relevant=True).count()
    if total_persons == 0:
        return
        
    for values in iter_entities_from(filename):
        # primero vemos si la persona esta
        try:
            person = models.Person.objects.get(uri=values['resource'])
        except models.Person.DoesNotExist:
            #print values['resource'], 'not a recognized person'
            continue
            
        # do stuff
        func(person, values)
            
        i += 1
        
        if i == total_persons:
            break
    
# internal use

# n-triples
parser = re.compile('<(.+)>\s<(.+)>\s(.+)\s\.+')

# values
parser_value_string = re.compile('"(.+)"@en')
parser_value = re.compile('"(.+)"\\^\\^<.+>')
parser_resource = re.compile('<(.+)>')

def parse_attrib(uri):
    parts = uri.split('/')
    name = unquote(parts[-1])
    name = name.replace('_', ' ')
    return unicode(name.decode('unicode-escape', errors='ignore'))

def get_parts(line):
    parts = parser.match(line).group(1, 2, 3)
    resource = parts[0]
    subject = parse_attrib(parts[0])
    predicate = parse_attrib(parts[1])
    
    match_string = parser_value_string.match(parts[2])
    if match_string != None:
        obj = match_string.group(1)
    else:
        match_value = parser_value.match(parts[2])
        if match_value != None:
            obj = match_value.group(1)
        else:
            match_resource = parser_resource.match(parts[2])
            if match_resource != None:
                obj = match_resource.group(1)
            else:
                obj = None
            
        #print line
        #print predicate, ':', parts[2], '=>', obj
        
    if obj:
        obj = unicode(obj.decode('unicode-escape', errors='ignore'))
    
    return {'resource': resource, 'subject': subject, 'predicate': predicate, 'object': obj}

def get_attr(values, attr, default=None):
    try:
        return values[attr][0]
    except KeyError:
        return default
    
def get_date(values, attr):
    try:
        d = values[attr][0]
        parts = d.split('-')
    
        try:
            if len(parts) == 3:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d")
            elif len(parts) == 2:
                dt = datetime.datetime.strptime(d, "%Y-%m")
            elif len(parts) == 1:
                dt = datetime.datetime.strptime(d, "%Y")
            else:
                return None
        except ValueError:
            return None
    
        return dt
    except KeyError:
        return None