from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.urlresolvers import get_script_prefix

#standard lib
import json
from pprint import pprint as pp
import urllib
import urlparse

from utils import JSONResponseMixin
import py360link as sersol

#Default sersol key
from app_settings import SERSOL_KEY

"""
Examples

article
http://localhost:8000/?sid=google&auinit=S&aulast=Hammond&atitle=Agent+Orange:+Health+and+Environmental+Issues+in+Vietnam,+Cambodia,+and+Laos&id=doi:10.1002/9781118184141.ch15

inbook
http://localhost:8000/?genre=bookitem&isbn=9781405156967&title=Autism%3a+An+integrated+view+from+neurocognitive%2c+clinical%2c+and+intervention+research.&volume=&issue=&date=20080101&atitle=Teaching+adults+with+autism+spectrum+conditions+to+recognize+emotions%3a+Systematic+training+for+empathizing+difficulties.&spage=236&pages=236-259&sid=EBSCO:PsycINFO&aulast=Golan%2c+Ofer

journal
http://localhost:8000/?sid=FirstSearch%3AWorldCat&genre=journal&issn=2151-0814&title=Charter+school+law+deskbook.&id=doi%3A&pid=%3Caccession+number%3E436869608%3C%2Faccession+number%3E%3Cfssessid%3E0%3C%2Ffssessid%3E&url_ver=Z39.88-2004&rfr_id=info%3Asid%2Ffirstsearch.oclc.org%3AWorldCat&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&req_dat=%3Csessionid%3E0%3C%2Fsessionid%3E&rfe_dat=%3Caccessionnumber%3E436869608%3C%2Faccessionnumber%3E&rft_id=info%3Aoclcnum%2F436869608&rft_id=urn%3AISSN%3A2151-0814&rft.jtitle=Charter+school+law+deskbook.&rft.issn=2151-0814&rft.place=Charlottesville++VA&rft.pub=LexisNexis&rft.genre=journal&checksum=25d304e7598efe59760d18e8854b5090&title=Brown%20University&linktype=openurl&detail=RBN
http://localhost:8000/?genre=journal&issn=0036-8075&date=1995

"""

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
        from bibjsontools import to_openurl, from_openurl
        from utils import merge_bibjson
        context = super(ResolveView, self).get_context_data(**kwargs)
        query = self.request.META.get('QUERY_STRING', None)
        if self.sersol_key != SERSOL_KEY:
            context['customer'] = self.sersol_key
        if not query:
            self.template_name = 'resolver/index.html'
            return context
        #Return an index page if query isn't found. 
        if not query:
        	return context
        resp = sersol.get(query, key=self.sersol_key, timeout=10)
        data = resp.json()
        #Use the first bib only now.
        this_bib = data.get('records', [])[0]
        orig_bib = from_openurl(query)
        citation = merge_bibjson(orig_bib, this_bib)

        #shortcut some values
        links = citation.get('links')
        ids = citation.get('identifier', [])

        citation['doi'] = self.get_identifer(ids, 'doi')
        citation['oclc'] = self.get_identifer(ids, 'oclc')
        citation['issn'] = self.get_identifer(ids, 'issn')
        context['citation'] = citation
        #links = resolved.link_groups
        #do we have a link to full text?
        context['has_full_text'] = self.has_full_text(links)
        #context['links'] = links
        print citation
        citation_type = citation.get('type')
        if citation_type == 'inbook':
            citation_type = 'book section'
        context['type'] = citation_type
        context['rfr'] = citation.get('_rfr', 'unknown')
        context['library'] = data.get('metadata', {}).get('library')
        context['openurl'] = to_openurl(citation) + '&url_ver=Z39.88-2004'
        context['permalink'] = self.permalink(ids)
        context['bib'] = json.dumps(data)
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

    def permalink(self, identifiers):
        """
        Create permalinks for OpenURLs that resolve to citations with PMIDs or DOIs.
        """
        base = "http://%s%s" % (self.request.META.get('HTTP_HOST').rstrip('/'),
                                 self.request.META.get('PATH_INFO').rstrip('/'))
        for identifier in identifiers:
            if identifier.get('type') == 'pmid':
                return "%s/?pmid=%s" % (base, identifier.get('id'))
            elif identifier.get('type') == 'doi':
                return "%s/?doi=%s" % (base, identifier.get('id'))
            else:
                #To create permalinks for other metadata you could add a view that will save the OpenURL
                #to a database and assign a short link, e.g. '/get/b23', that would resolve
                #that url when accessed again.  
                return



