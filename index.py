# -*- coding: utf-8 -*-
import sys
import time

try:
    import settings # Assumed to be in the same directory.
    #settings.DISABLE_TRANSACTION_MANAGEMENT = True
except ImportError:
    sys.exit(1)

import json
import django
import django.core.management
django.core.management.setup_environ(settings)

from profiles.models import *

from whoosh.index import create_in
from whoosh.fields import *
schema = Schema(
    description=TEXT(stored=True, phrase=False), 
    title=TEXT(stored=True), 
    id=ID(stored=True), 
    type=TEXT(stored=True),
    score=NUMERIC(stored=True),
    score_range=NUMERIC(stored=True),
    avatar=STORED()
)

ix = create_in(settings.WHOOSH_INDEX_DIR, schema)
writer = ix.writer()

users = Person.objects.filter(is_relevant=True).exclude(name='')
total_users = users.count()

for i in xrange(0, total_users, 10000):
    end = i + 10000
    #print i, end
    
    for u in users[i:end]:
        print u.name
        try:
            abstract = u.personmeta_set.filter(meta_name='abstract')[0].meta_value
        except Exception:
            abstract = ''
            
        indexed = u.name + u' ' + abstract
        score_range = u.score/5
        if score_range > 39:
            score_range = 39
            
        print indexed
        writer.add_document(description=indexed, title=u.name, id=unicode(u.id), type=u'profile', score=u.score, score_range=score_range, avatar=u.depiction)

categories = Category.objects.filter(count__gt=1).exclude(name='')
total_categories = categories.count()

for i in xrange(0, total_categories, 10000):
    end = i + 10000
    
    for c in categories[i:end]:
        print c.name
        
        score_range = c.avg_score/5
        if score_range > 39:
            score_range = 39
        
        writer.add_document(description=c.name, title=c.name, id=unicode(c.id), type=u'category', score=c.avg_score, score_range=score_range)

writer.commit()
