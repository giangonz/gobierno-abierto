from django.contrib import admin
from .models import Category, DataPoint

admin.site.register(Category, admin.ModelAdmin)
admin.site.register(DataPoint, admin.ModelAdmin)
