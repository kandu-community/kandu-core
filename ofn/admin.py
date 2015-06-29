import requests

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ofn.models import Profile, Product, Variant

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args,**kwargs)

        # params = { 'token': self.instance.token }
        # r = requests.get(settings.OFN['url'] + '/api/enterprises/managed', params=params)
        
        # if r.status_code == 200:
        #     choices = [[ int(e['id']), e['name'] ] for e in r.json()]
        #     self.fields['supplier_id'] = forms.IntegerField(widget=forms.Select(choices=choices), label='Supplier')

    class Meta:
        model = Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileForm
    can_delete = False
    verbose_name_plural = 'ofn'

class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        # params = { 'token': settings.OFN['token'] }
        # r = requests.get(settings.OFN['url'] + '/api/taxonomies/%s' % settings.OFN['taxonomy_id'] + '/taxons', params=params)
        
        # if r.status_code == 200:
        #     choices = [[ int(e['id']), e['name'] ] for e in r.json()]
        #     self.fields['primary_taxon_id'] = forms.IntegerField(widget=forms.Select(choices=choices), label='Taxon')

    class Meta:
        model = Product

class VariantInline(admin.TabularInline):
    model = Variant
    readonly_fields = ('remote_id', 'updated_at')

class ProductAdmin(admin.ModelAdmin):
    inlines = (VariantInline,)
    form = ProductForm
    ordering = ('user', 'name',)
    list_display = ('user', 'name',)
    readonly_fields = ('remote_id', 'updated_at')

admin.site.register(Product, ProductAdmin)
