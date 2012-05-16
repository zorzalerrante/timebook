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

from django.db.models import Q
from django.db import transaction
import profiles.models

#person_count = profiles.models.Person.objects.all().count()
#movement_base = person_count + 1

with open('edges.csv', 'w') as f:
    
    f.write('{0}\t{1}\t{2}\t{3}\n'.format('Source', 'Target', 'Weight', 'Type'))
    
    rels = profiles.models.Relation.objects.all()
    total_rels = rels.count()
    for i in xrange(0, total_rels, 1000):
        for r in rels[i:i+1000]:
            f.write('{0}\t{1}\t{2}\t{3}\n'.format(r.source_id, r.target_id, 1.0, 'Directed'))
        
    #persons = profiles.models.Person.objects.filter(is_relevant=True)
    #total_persons = persons.count()
'''
    for i in xrange(0, total_persons, 1000):
        for p in persons[i:i+1000]:
            #print '{0}\t{1}\t{2}\t{3}\n'.format(.group.id + movement_base, a.person.id, 1.0, 'Directed')
            values = p.groups.values_list('id')
            #print values
            for v in values:
                #print v[0], p.id
                f.write('{0}\t{1}\t{2}\t{3}\n'.format(v[0] + movement_base, p.id, 1.0, 'Directed'))
                f.write('{0}\t{1}\t{2}\t{3}\n'.format(p.id, v[0] + movement_base, 1.0, 'Directed'))
  
'''
    
with open('nodes.csv', 'w') as f:
    f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format('ID', 'Name', 'Birth', 'Death', 'Person'))
    v', 'w') as f:
 with open('nodes.csv', 'w') as f:
     f.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format('ID', 'Name', 'Birth', 'Death', 'Person'))
     

    persons = profiles.models.Person.objects.filter(is_relevant=True)
    for p in persons:
        #rel_count = profiles.models.PersonRelation.objects.filter(Q(source=p)|Q(target=p)).count()
        #if rel_count == 0:
            #print "skipped", p.name
            #continue
        #print p.name, rel_count
        f.write('{0}\t"{1}"\t{2}\n'.format(p.id, p.name.replace('"', '').encode('utf-8', errors='ignore'), 'P'))

    '''
    groups = profiles.models.Category.objects.all()
    for g in groups:
        #print g.name
        f.write('{0}\t"{1}"\t{2}\n'.format(g.id + movement_base, g.name.replace('"', '').encode('utf-8', errors='ignore'), 'M'))
    '''
     
    
