from django.db import models

import jsonfield

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


class PrintTitle(models.Model):
    """
    Basic model for storing print serial holdings.
    """
    issn = models.CharField(max_length=15)
    start = models.IntegerField()
    end = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=25, blank=True, null=True)
    call_number = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return "%s %s to %s" % (self.issn, self.start, self.end)
