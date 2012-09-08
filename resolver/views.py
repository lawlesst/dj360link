from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.urlresolvers import get_script_prefix

#standard lib
import json
import urllib
import urlparse

from utils import JSONResponseMixin
from py360link import get_sersol_data, Resolved


SERSOL_KEY = 'rl3tp7zf5x'

class ResolveView(TemplateView, JSONResponseMixin):
    template_name = 'resolver/resolve.html'
    default_json = True
    
    def get(self, request, **kwargs):
    	return super(ResolveView, self).get(request)

    def get_context_data(self, **kwargs):
    	"""
    	Handle the request and return the 'resolver' to the user.
    	"""
        context = super(ResolveView, self).get_context_data(**kwargs)
        query = self.request.META.get('QUERY_STRING', None)
        #Return an index page if query isn't found. 
        if not query:
        	return context
        sersol_data = get_sersol_data(query, key=SERSOL_KEY)
        resolved = Resolved(sersol_data)
        context['citation'] = resolved.citation
        context['links'] = resolved.link_groups
        context['type'] = resolved.format
        return context

    def render_to_response(self, context):
    	"""
    	Will render the response as HTML or JSON.
    	"""
        # Look for a 'output=json' GET argument  
        if (self.request.GET.get('output','html') == 'json')\
            or (self.default_json):
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return super(ResolveView, self).render_to_response(context)

