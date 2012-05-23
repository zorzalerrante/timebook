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

# aggregators
from django.db.models import Min, Max

# categories 
from profiles.models import Category 

categories = Category.objects.all()
total_count = categories.count()
#total_count = 100

for i in xrange(0, total_count, 1000):
    for cat in categories[i:i+1000]:
        cat.count = cat.person_set.count()
        cat.min_year = cat.person_set.aggregate(Min('birth_year'))['birth_year__min']
        cat.max_year = cat.person_set.aggregate(Max('birth_year'))['birth_year__max']
        print cat.pk, cat.name, cat.person_set.count(), cat.min_year, cat.max_year
        cat.save()
        

