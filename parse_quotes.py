# -*- coding: utf-8 -*-
import bz2
from urllib import unquote
import re

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
import profiles.models

from xml.sax import make_parser, handler

def analyseEntry(content):
	#print content
	sourceStart = len(content)
	sourceEnd = len(content)
	sourceFound = False
	for m in re.finditer(r"==\s*([^=\s]+)\s*==\n", content):
		if (m.group(1).lower() == 'sourced'):
			#Found source block
			sourceStart = m.start()
			sourceFound = True
		elif (sourceFound == True):
			#Conclude source
			sourceEnd = m.start();
			break
		
	sourced = content[sourceStart:sourceEnd]
	
#	print sourceStart, sourceEnd
#	print sourced
	citations = []
	citation = None
	descriptionFound = False
	
	for line in sourced.split("\n"):
		citationMatch = re.match(r"\s*\*\s+'''(.+)'''", line)
		descriptionMatch = re.match(r"\s*\*\*\s+(.+)", line)
		if (citationMatch):
#			print citation
			citation = {
				'text': None,
				'description': None,
				'date': None,
			}
			citations.append(citation)
			citation['text'] = citationMatch.group(1)

		elif (descriptionMatch and citation != None and citation['description'] == None):
			description = descriptionMatch.group(1)
			citation['description'] = description
			date = None
			for dateCandidate in re.finditer(r'\(([^\)]+)\)', description):
				dateStr = dateCandidate.group(1)
				#print dateStr
				formats = [
					"%Y",
					 "%B %Y",
					"%b %Y",
					"%d %b %Y"
					]
				for format in formats:
					try:
						date = time.strptime(dateStr, format)
						citation['date'] = date
						break;
					
					except ValueError:
						pass
				#We want only the first candidate...
				break
	return citations


class FancyCounter(handler.ContentHandler):

    def __init__(self):
        self.in_title_ = False
        self.in_content_ = False
        self.title = ''
        self.content = ''
        self.processed = 0

    def startElement(self, name, attrs):
	self.in_title_ = bool(name == 'title')
	self.in_content_ = bool(name == 'text')
	
	if name == 'page':
	    self.title = ''
	    self.content = ''
            
    def endElement(self, name):
	if name == 'page':
	    self.title = self.title.strip()
	    self.processed += 1
	    content = self.content;
	    print self.title
	    citations = analyseEntry (content)
	    #print citations
	    
	    if citations:
		persons = profiles.models.Person.objects.filter(name=self.title)
		if persons:
		    person = persons[0]
		    for q in citations:
			if q['date']:
			    q['date'] = datetime.date(q['date'][0], q['date'][1], q['date'][2])
			print q
			quote = profiles.models.Quote(author=person, text=q['text'], date=q['date'], description=q['description'])
			quote.save()
		

    def endDocument(self):
        pass
      
    def characters(self, content):
	if self.in_title_:
	    self.title += content
	if self.in_content_:
	    self.content += content

            
parser = make_parser()
dump = open('dbpediadata/enwikiquote-20110523-pages-meta-current.xml', 'r')

parser.setContentHandler(FancyCounter())
parser.parse(dump)
dump.close()