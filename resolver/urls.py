from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls.defaults import *

from views import ResolveView
#from app_settings import PERMALINK_PREFIX

urlpatterns = patterns('', 
    #Optional 360Link key
    url(r'^(?P<sersol_key>[a-z0-9]+)/$', ResolveView.as_view(), name='resolve_view'),
    url(r'^$', ResolveView.as_view(), name='resolve_view'),
)