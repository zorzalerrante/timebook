from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    (r'^api/profile/(?P<profile_id>\d+)/$', 'views.rest_profile'),
    (r'^api/category/(?P<category_id>\d+)/$', 'views.rest_category'),
    (r'^api/search/', 'views.rest_search'),
    (r'^api/explore/', 'views.rest_explore'),
    (r'^api/user/login/', 'fbusers.views.login')
)

if settings.USE_DJANGO_SERVER:

    urlpatterns.extend(patterns('',
        (r'^site/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.TIMEBOOK_DIR + '/site'})
    ))
    
    print urlpatterns


