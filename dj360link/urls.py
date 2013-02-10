from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import resolver

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'h360link.views.home', name='home'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('resolver.urls', namespace='resolver')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 
        'django.views.static.serve', 
        {'document_root': settings.STATIC_ROOT}),
    )