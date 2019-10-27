from django.contrib import admin

# Register your models here.
from projects_app.models import *


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    list_display = 'name link is_active'.split()
    list_editable = 'is_active'.split()


admin.site.register(Project, ProjectAdmin)
admin.site.register(Brand)
admin.site.register(TrendYolDepartment)
admin.site.register(TrendYolCategory)

