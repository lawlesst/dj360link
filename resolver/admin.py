from django.contrib import admin
from models import Resource

class ResourceAdmin(admin.ModelAdmin):
    search_fields = ['id', 'bib']
    list_display = ['id', 'bib', 'created_at', 'modified_at']
    list_filter = ['created_at', 'modified_at']
    pass
admin.site.register(Resource, ResourceAdmin)