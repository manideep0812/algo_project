from django.contrib import admin
from problems.models import problem
from django.utils.html import format_html
from django.db import models


# Register your models here.
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview')
    search_fields = ('name', 'description')
    
    def description_preview(self, obj):
        # Replace newlines with <br> tags for display in the list view
        return format_html('<div style="white-space: pre-wrap;">{}</div>', obj.description)
    description_preview.short_description = 'Description'
    
    # Use a Textarea widget for the description field
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 10, 'style': 'font-family: monospace;'})},
    }


admin.site.register(problem, ProblemAdmin)