from django.template import Context, loader
from fbusers.models import *

from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.cache import cache
from django.template import RequestContext
from django.utils.html import strip_tags
from django.db.models import Q

import datetime
import json
import facebook

def render_json(request, data):
    return render_to_response('templates/json.html', {'json': json.dumps(data)}, context_instance=RequestContext(request))

def build_result(fbuser):
    result = {
        'status': 'ok',
        'data': {
            'name': fbuser.name,
            'uid': fbuser.facebook_id,
            'recommendations': []
        }
    }
    
    return result

def login(request):
    result = {'status': 'error', 'data': {}}
    
    if request.method == 'GET': 
        uid = request.GET['uid']        
        user = facebook.get_user_from_cookie(request.COOKIES, '191272084277793', '154c4809e648c40950ec50c24d0c5736')
        #print user
        if user:
            graph = facebook.GraphAPI(user['access_token'])
            profile = graph.get_object("me")
            
            try:
                fbuser = User.objects.get(pk=profile['id'])
                result = build_result(fbuser)
            except User.DoesNotExist:
                fbuser = User()
                fbuser.read_json(profile)
                fbuser.save()
                
                result = build_result(fbuser)
                
                #print graph
                #print profile
            
                #connections = ['interests', 'friends', 'likes', 'music', 'movies', 'books']
                #for conn in connections:
                    #print conn
                    #items = graph.get_connections("me", conn)
                    #print items
            
    return render_json(request, result)