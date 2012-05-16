# -*- coding: utf-8 -*-
import sys
import time
import datetime

import settings

import django
import django.core.management
import django.core.exceptions
django.core.management.setup_environ(settings)

from django.db.models import Q
from django.db import transaction
import profiles.models

import json
import networkx as nx


'''
this file creates a directed graph in networkx using the person connectivity 
from timebook. then we calculate pagerank and save the results in a json file.
'''

graph = nx.DiGraph()
   
rels = profiles.models.Relation.objects.all()
total_rels = rels.count()

# we do this loop to avoid loading the entire dataset in memory
for i in xrange(0, total_rels, 1000):
    for r in rels[i:i+1000]:
        graph.add_edge(r.source_id, r.target_id)
    
pagerank = nx.pagerank(graph)

with open('pagerank.json', 'w') as f:
    json.dump(pagerank, f)

graph.clear()


