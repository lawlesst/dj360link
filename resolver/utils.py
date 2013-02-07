"""
Helpers
"""
from django.http import HttpResponse
import json

class JSONResponseMixin(object):
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


