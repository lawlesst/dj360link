from django.db import models

import jsonfield    

from datetime import datetime
#local
from app_settings import PERMALINK_PREFIX
from utils import base62

class Resource(models.Model):
    query = models.TextField()
    bib = jsonfield.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    @models.permalink    
    def get_absolute_url(self):
        tiny = base62.from_decimal(self.id)
        return ('resolver:permalink', (),
                {'tiny': tiny})

    def __unicode__(self):
        return unicode(self.id)
