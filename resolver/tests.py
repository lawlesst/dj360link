"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from pprint import pprint as pp

class Link360Test(TestCase):
    def test_get_data(self):
        """
        """
        import py360link
        from app_settings import SERSOL_KEY
        ss_key = SERSOL_KEY 
        data = py360link.get('pmid=22811347', key=SERSOL_KEY)
        results = data.json()
        bib = results['records'][0]
        self.assertEqual(bib['type'], 'article')



