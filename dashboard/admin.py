from django.contrib import admin
from django import forms
from django.core.urlresolvers import reverse
from .models import Category, DataPoint


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'enabled', 'date_disabled']


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    form = CategoryForm
    list_display = ('name', 'enabled')
    view_on_site = False

    prepopulated_fields = {'slug': ('name', )}

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if obj:
            if obj.enabled:
                self.exclude = ['date_disabled']
        else:
            self.exclude = ['date_disabled']
        return super(CategoryAdmin, self).get_form(request, obj, **kwargs)

    # def view_on_site(self, obj):
    #     return reverse('category', kwargs={'slug': obj.slug})


class DataPointForm(forms.ModelForm):
    class Meta:
        model = DataPoint
        fields = ['name', 'category', 'resource', 'slug', 'enabled', 'date_disabled', 'date_field',
                  'data_field', 'trend_upwards_positive', 'featured']


class DataPointAdmin(admin.ModelAdmin):
    model = DataPoint
    form = DataPointForm
    list_display = ('name', 'category', 'featured')

    prepopulated_fields = {'slug': ('name', )}

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if obj:
            if obj.enabled:
                self.exclude = ['date_disabled']
        else:
            self.exclude = ['date_disabled']
        return super(DataPointAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Category, CategoryAdmin)
admin.site.register(DataPoint, DataPointAdmin)
