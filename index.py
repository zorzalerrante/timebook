# -*- coding: utf-8 -*-
import sys
import time

try:
    import settings # Assumed to be in the same directory.
    #settings.DISABLE_TRANSACTION_MANAGEMENT = True
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

import json
import django
import django.core.management
django.core.management.setup_environ(settings)

from profiles.models import *

from whoosh.index import create_in
from whoosh.fields import *
schema = Schema(names=TEXT, title=TEXT(stored=True), id=ID(stored=True), type=TEXT(stored=True))

ix = create_in(settings.WHOOSH_INDEX_DIR, schema)
writer = ix.writer()

users = Person.objects.filter(is_relevant=True)
total_users = users.count()

for i in xrange(0, total_users, 10000):
    end = i + 10000
    #print i, end
    
    for u in users[i:end]:
        print u.name
        indexed = u.name
        writer.add_document(names=u.name, title=u.name, id=unicode(u.id), type=u'profile')

categories = Category.objects.filter(count__gt=1)
total_categories = categories.count()

for i in xrange(0, total_categories, 10000):
    end = i + 10000
    
    for c in categories[i:end]:
        print c.name
        writer.add_document(names=c.name, title=c.name, id=unicode(c.id), type=u'category')

writer.commit()
