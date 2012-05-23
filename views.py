# Create your views here.
from django.template import Context, loader
from profiles.models import *
from profiles.forms import SearchForm
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.cache import cache
from django.template import RequestContext
from django.utils.html import strip_tags
from django.db.models import Q
from django.core import serializers

import datetime
import json

import search

def render_json(request, data):
    return render_to_response('json.html', {'json': json.dumps(data)}, context_instance=RequestContext(request), mimetype='application/json')
    
def prepare_resource_json(resource):
    return json.loads(serializers.serialize("json", [resource]))[0]
    #return {'id': resource.id, 'name': resource.name, 'uri': resource.uri}
    

def rest_profile(request, profile_id):
    profile = get_object_or_404(Person, pk=profile_id)

    connections = Relation.objects.filter(Q(source=profile)|Q(target=profile)).select_related()
    
    following = []
    followers = []
    
    for relation in connections:
        if relation.source == profile:
            following.append(relation.target)
        else:
            followers.append(relation.source)
    
    groups = profile.groups.all()
    meta = PersonMeta.objects.filter(person=profile)
    
    abstract = ''
    
    for m in meta:
        if m.meta_name == 'abstract':
            abstract = json.loads(m.meta_value)
    c = prepare_resource_json(profile)
    
    c['following'] = [prepare_resource_json(f) for f in following]
    c['followers'] = [prepare_resource_json(f) for f in followers]
    c['groups'] = [prepare_resource_json(g) for g in groups]
    c['meta'] = [{'key': m.meta_name, 'value': json.loads(m.meta_value)} for m in meta]
    c['abstract'] = abstract
    
    # TODO: here we should add a decorator mechanism or something similar for applications to add their information
    c['works'] = [prepare_resource_json(w) for w in profile.work_set.all()]
    c['quotes'] = [prepare_resource_json(w) for w in profile.quote_set.all()]
    
    return render_json(request, c)
    
    
def rest_category(request, category_id):
    group = get_object_or_404(Category, pk=category_id)
    members = group.person_set.all()

    json_serializer = serializers.get_serializer("json")

    c = prepare_resource_json(group)
    c['members'] = json.loads(serializers.serialize("json", members))
    
    return render_json(request, c)
    
    
def rest_search(request):
    results = {'query': '', 'results': []}
    if request.method == 'GET': 
        form = SearchForm(request.GET)
        if form.is_valid(): 
            query = form.cleaned_data['query'].strip() + '*'
            hits = search.perform_search(query)

            results['query'] = form.cleaned_data['query']

            if hits:
                for h in hits:
                    results['results'].append({'id': h['id'], 'name': h['title'], 'uri': '', 'type': h['type']})

    return render_json(request, results['results'])
