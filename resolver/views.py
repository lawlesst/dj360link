from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.urlresolvers import get_script_prefix

#standard lib
import json
import urllib
import urlparse

from utils import JSONResponseMixin
from py360link import get_sersol_data, Resolved

#Default sersol key
from app_settings import SERSOL_KEY

class ResolveView(TemplateView, JSONResponseMixin):
    template_name = 'resolver/resolve.html'
    default_json = False
    sersol_key = SERSOL_KEY
    
    def get(self, request, **kwargs):
        #pull sersol key from kwargs if it's there
        skey = kwargs.get('sersol_key', None)
        if skey:
            self.sersol_key = skey
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
        sersol_data = get_sersol_data(query, key=self.sersol_key)
        resolved = Resolved(sersol_data)
        context['citation'] = resolved.citation
        links = resolved.link_groups
        #do we have a link to full text?
        context['has_full_text'] = self.has_full_text(resolved.link_groups)
        context['links'] = links
        context['type'] = resolved.format
        context['library'] = resolved.library
        context['openurl'] = resolved.openurl
        context['permalink'] = self.permalink(resolved.citation)
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

    def has_full_text(self, links):
        """
        Loop through sersol returned links and determine if full text
        to the source exists.
        """
        for link in links:
            if link['url'].get('article'):
                return True
        return False

    def permalink(self, citation):
        """
        Create permalinks for OpenURLs that resolve to citations with PMIDs or DOIs.
        """
        base = "http://%s%s" % (self.request.META.get('HTTP_HOST').rstrip('/'),
                                 self.request.META.get('PATH_INFO').rstrip('/'))
        if citation.get('pmid'):
            return "%s/?pmid=%s" % (base, citation.get('pmid'))
        elif citation.get('doi'):
            return "%s/?doi=%s" % (base, citation.get('doi'))
        else:
            #To create permalinks for other metadata you could add a view that will save the OpenURL
            #to a database and assign a short link, e.g. '/get/b23', that would resolve
            #that url when accessed again.  
            return



