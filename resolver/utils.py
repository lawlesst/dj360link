"""
Helpers
"""
from django.http import HttpResponse
from django.views.generic import TemplateView
import json

def merge_bibjson(a, b) :
    def _merge(a, b):
        #https://github.com/okfn/bibserver/blob/bibwiki/bibserver/dao.py
        for k, v in a.items():
            if k.startswith('_') and k not in ['_collection']:
                pass
            if isinstance(v, dict) and k in b:
                merge_bibjson(v, b[k])
            elif isinstance(v, list) and k in b:
                if not isinstance(b[k], list):
                    b[k] = [b[k]]
                for idx, item in enumerate(v):
                    if isinstance(item,dict) and idx < len(b[k]):
                        merge_bibjson(v[idx],b[k][idx])
                    elif item not in b[k]:
                        b[k].append(item)
        a.update(b)
        return a

    out = _merge(a, b)
    return out



#===============================================================================
#Base views. 
#===============================================================================
class JSONResponseMixin(object):
    """
    JSON Response mixin to allow for JSON serialization
    of various views..
    """
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        params = self.request.GET
        if params.has_key('callback'):
            content = "%s(%s)" % (params['callback'], content)
        return HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: this needs to be better to ensure that you are seralizing what
        # is needed as JSON.  For now just popping known problems.
        #Also see - https://docs.djangoproject.com/en/dev/topics/serialization/
        remove = ['user', 'resource', 'profile']
        for rem in remove:
            try:
                del context[rem]
            except KeyError:
                pass
        return json.dumps(context)

class BaseResolverView(TemplateView, JSONResponseMixin):
    """
    Base view for all in resolver app.
    """
    def render_to_response(self, context):
        """
        Will render the response as HTML or JSON.
        """
        # Look for a 'output=json' GET argument  
        if (self.request.GET.get('output','html') == 'json')\
            or (self.default_json):
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return super(BaseResolverView, self).render_to_response(context)


#===============================================================================
# For short URLs.  Implementation based off: 
# https://raw.github.com/jacobian/django-shorturls/master/src/shorturls/baseconv.py
#===============================================================================
class BaseConverter(object):
    """
    From: https://raw.github.com/jacobian/django-shorturls/master/src/shorturls/baseconv.py
    Will use this method of converting primary keys to short strings that can be used
    for permalinks rather than simply using the primary key.  See this discussion
    for reasons why primary key links aren't a great idea.
    http://stackoverflow.com/questions/566996/using-primary-key-id-field-as-an-identifier-in-a-url

    Convert numbers from base 10 integers to base X strings and back again.

    Original: http://www.djangosnippets.org/snippets/1431/

    Sample usage:

    >>> base20 = BaseConverter('0123456789abcdefghij')
    >>> base20.from_decimal(1234)
    '31e'
    >>> base20.to_decimal('31e')
    1234
    """
    decimal_digits = "0123456789"
    
    def __init__(self, digits):
        self.digits = digits
    
    def from_decimal(self, i):
        return self.convert(i, self.decimal_digits, self.digits)
    
    def to_decimal(self, s):
        return int(self.convert(s, self.digits, self.decimal_digits))
    
    def convert(number, fromdigits, todigits):
        # Based on http://code.activestate.com/recipes/111286/
        if str(number)[0] == '-':
            number = str(number)[1:]
            neg = 1
        else:
            neg = 0

        # make an integer out of the number
        x = 0
        for digit in str(number):
           x = x * len(fromdigits) + fromdigits.index(digit)
    
        # create the result in base 'len(todigits)'
        if x == 0:
            res = todigits[0]
        else:
            res = ""
            while x > 0:
                digit = x % len(todigits)
                res = todigits[digit] + res
                x = int(x / len(todigits))
            if neg:
                res = '-' + res
        return res
    convert = staticmethod(convert)

bin = BaseConverter('01')
hexconv = BaseConverter('0123456789ABCDEF')
base62 = BaseConverter(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
)
