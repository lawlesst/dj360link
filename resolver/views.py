from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.core.urlresolvers import get_script_prefix

#standard lib
import json
import logging
from pprint import pprint as pp
import urllib
import urlparse

# Get an instance of a logger
logger = logging.getLogger(__name__)

from utils import BaseResolverView
import py360link as sersol

#Default sersol key
from app_settings import SERSOL_KEY

from models import Resource

"""
Examples

article
http://localhost:8000/?sid=google&auinit=S&aulast=Hammond&atitle=Agent+Orange:+Health+and+Environmental+Issues+in+Vietnam,+Cambodia,+and+Laos&id=doi:10.1002/9781118184141.ch15

inbook
http://localhost:8000/?genre=bookitem&isbn=9781405156967&title=Autism%3a+An+integrated+view+from+neurocognitive%2c+clinical%2c+and+intervention+research.&volume=&issue=&date=20080101&atitle=Teaching+adults+with+autism+spectrum+conditions+to+recognize+emotions%3a+Systematic+training+for+empathizing+difficulties.&spage=236&pages=236-259&sid=EBSCO:PsycINFO&aulast=Golan%2c+Ofer

journal
http://localhost:8000/?sid=FirstSearch%3AWorldCat&genre=journal&issn=2151-0814&title=Charter+school+law+deskbook.&id=doi%3A&pid=%3Caccession+number%3E436869608%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E436869608%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F436869608&rft_id=urn%3AISSN%3A2151-0814&rft.jtitle=Charter+school+law+deskbook.&rft.issn=2151-0814&rft.place=Charlottesville++VA&rft.pub=LexisNexis&rft.genre=journal&checksum=25d304e7598efe59760d18e8854b5090&title=Brown%20University&linktype=openurl&detail=RBN
http://localhost:8000/?genre=journal&issn=0036-8075&date=1995

crossref content negotiation
http://crosstech.crossref.org/2011/11/turning_dois_into_formatted_ci.html

failing resolution
http://localhost:8000/?doi=10.1177/1527002507808309

"""

class ResolveView(BaseResolverView):
    template_name = 'resolver/resolve.html'
    default_json = False
    sersol_key = 'rl3tp7zf5x'


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
        from bibjsontools import to_openurl, from_openurl
        from utils import merge_bibjson
        context = super(ResolveView, self).get_context_data(**kwargs)
        #Check to see if a resource is set for this view.
        #This will happen when a permalink is being requested.
        this_resource = getattr(self, 'resource', None)
        if self.sersol_key != SERSOL_KEY:
            context['customer'] = self.sersol_key

        query = self.request.META.get('QUERY_STRING', None)
        if (not query) and (not this_resource):
            self.template_name = 'resolver/index.html'
            return context
        if this_resource:
            citation = this_resource.bib
            openurl = to_openurl(citation)
        else:
            cached_sersol = cache.get(query)
            if cached_sersol:
                data = cached_sersol

            else:
                resp = sersol.get(query, key=self.sersol_key, timeout=10)
                try:
                    data = resp.json()
                except sersol.Link360Exception, e:
                    logger.error("%s -- %s" % (query, e))
                    return HttpResponseServerError(e)
                cache.set(query, data, 300)
            #Use the first bib only now.
            this_bib = data.get('records', [])[0]
            this_bib['_library'] = data.get('metadata', {}).get('library')
            orig_bib = from_openurl(query)
            citation = merge_bibjson(orig_bib, this_bib)
            #generate a new openurl based on merged bibjson objects
            openurl = to_openurl(citation)
        
        #shortcut some values
        links = citation.get('links')
        ids = citation.get('identifier', [])
        doi = self.get_identifer(ids, 'doi')
        citation['doi'] = doi
        citation['oclc'] = self.get_identifer(ids, 'oclc')
        citation['issn'] = self.get_identifer(ids, 'issn')
        citation_type = citation.get('type')
        if citation_type == 'inbook':
            citation_type = 'book section'
        context['citation'] = citation
        #links = resolved.link_groups
        #do we have a link to full text?
        context['has_full_text'] = self.has_full_text(links)
        context['type'] = citation_type
        context['rfr'] = citation.get('_rfr', 'unknown')
        context['library'] = citation.get('_library')
        citation['_openurl'] = openurl
        context['openurl'] =  openurl + '&url_ver=Z39.88-2004'
        return context

    def has_full_text(self, links):
        """
        Loop through sersol returned links and determine if full text
        to the source exists.
        """
        if links is None:
            return
        for link in links:
            if link['type'] == 'article':
                return True
        return False

    def get_identifer(self, identifiers, id_type):
        for idnt in identifiers:
            if idnt.get('type') == id_type:
                return idnt.get('id')
        return

class PermalinkView(ResolveView):
    template_name = 'resolver/resolve.html'
    default_json = False
    
    def get(self, request, **kwargs):
        from utils import base62
        #pull permalink key from kwargs if it's there
        plink = kwargs.get('tiny', None)
        rid = base62.to_decimal(plink)
        #Get the resource.  Account for possibility of two queries matching.
        resource = Resource.objects.get(id=rid)
        self.resource = resource
        self.is_permalink = True
        return super(PermalinkView, self).get(request)

    def post(self, *args, **kwargs):
        from bibjsontools import from_openurl
        out = {}
        posted = self.request.POST
        bib = json.loads(posted.get('bib'))
        #Get or create a resource for the given query.
        try:
            resource, created = Resource.objects.get_or_create(bib=bib)
        except MultipleObjectsReturned:
            resource = Resource.objects.filter(bib=bib)[0]
            created = False
        resource.save()
        base = "http://%s" % (self.request.META.get('HTTP_HOST').rstrip('/'))
        out['permalink'] = base + resource.get_absolute_url()
        return HttpResponse(json.dumps(out), mimetype='application/json')

    def get_context_data(self, **kwargs):
        context = super(PermalinkView, self).get_context_data(**kwargs)
        context['permalink_view'] = True
        return context