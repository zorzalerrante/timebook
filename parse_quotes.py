# -*- coding: utf-8 -*-

import sys
import settings # Assumed to be in the same directory.

import django
import django.core.management
import django.core.exceptions
django.core.management.setup_environ(settings)

import quotes.wikiquote
            
dump = settings.WIKIQUOTE_DUMPS_DIR + '/enwikiquote-20120519-pages-meta-current.xml.bz2'

importer = quotes.wikiquote.WikiquoteImporter()

importer.process(dump)
