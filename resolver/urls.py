from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.defaults import *

from views import ResolveView, PermalinkView
from app_settings import PERMALINK_PREFIX

urlpatterns = patterns('', 
    #Optional 360Link key
    url(r'^(?P<sersol_key>[a-z0-9]+)/$', ResolveView.as_view(), name='resolve'),
    url(r'^get/%s(?P<tiny>.*)/$' % PERMALINK_PREFIX, PermalinkView.as_view(), name='permalink'),
    #All other OpenURLs
    url(r'^$', ResolveView.as_view(), name='resolve-view'),
)