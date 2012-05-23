# -*- coding: utf-8 -*-
import bz2
from urllib import unquote
from django.utils.http import urlquote
import re

import sys
import time
import datetime

import codecs

from django.db import transaction
import profiles.models
from models import Quote

from xml.sax import make_parser, handler


class WikiquoteHandler(handler.ContentHandler):
    def __init__(self):
        self.in_title_ = False
        self.in_content_ = False
        self.title = ''
        self.content = ''
        self.processed = 0

    def analyse_entry(self):
            #print content
            sourceStart = len(self.content)
            sourceEnd = len(self.content)
            sourceFound = False
            for m in re.finditer(r"==\s*([^=\s]+)\s*==\n", self.content):
                    if (m.group(1).lower() == 'sourced'):
                            #Found source block
                            sourceStart = m.start()
                            sourceFound = True
                    elif (sourceFound == True):
                            #Conclude source
                            sourceEnd = m.start();
                            break

            sourced = self.content[sourceStart:sourceEnd]

            citations = []
            citation = None
            descriptionFound = False

            for line in sourced.split("\n"):
                    citationMatch = re.match(r"\s*\*\s+'''(.+)'''", line)
                    descriptionMatch = re.match(r"\s*\*\*\s+(.+)", line)
                    if (citationMatch):
                            citation = {
                                    'text': '',
                                    'description': '',
                                    'date': None,
                            }
                            
                            citation['text'] = citationMatch.group(1)
                            citations.append(citation)

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
            citations = self.analyse_entry()
                
            if not citations:
                return
   
            print self.title
            
            try:
                uri = u'http://dbpedia.org/resource/' + urlquote(self.title.replace(u' ', u'_'))
                person = profiles.models.Person.objects.get(uri=uri)
            except profiles.models.Person.DoesNotExist:
                try:
                    person = profiles.models.Person.objects.get(name=self.title)
                #except profiles.models.Person.DoesNotExist:   
                except Exception:
                    print self.title, 'does not exists in the DB'
                    return
            
            imported = 0    
            
            for q in citations:
                if q['date']:
                    year = q['date'][0]
                else:
                    year = None
                
                quote = Quote(author=person, content=q['text'], year=year, source_name=q['description'])
                quote.save()

                #print person.name
                #print q['text']
                #print q['date']
                #print q['description']
                #print ''

            print 'imported quotes:', len(citations)

    def endDocument(self):
        pass

    def characters(self, content):
        if self.in_title_:
            self.title += content
        if self.in_content_:
            self.content += content

class WikiquoteImporter:
    def __init__(self):
        self.parser = make_parser()
        self.parser.setContentHandler(WikiquoteHandler())

    def process(self, dump_file_name):
        with bz2.BZ2File(dump_file_name, 'r') as dump:
            self.parser.parse(dump)

