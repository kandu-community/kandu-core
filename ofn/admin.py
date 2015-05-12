import requests

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ofn.models import Profile

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args,**kwargs)

        params = { 'token': self.instance.token }
        r = requests.get(settings.OFN_URL + '/api/enterprises/managed', params=params)
        
        if r.status_code == 200:
            choices = [[ int(e['id']), e['name'] ] for e in r.json()]
            self.fields['supplier_id'] = forms.IntegerField(widget=forms.Select(choices=choices), label='Supplier')

    class Meta:
        model = Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    form = ProfileForm
    can_delete = False
    verbose_name_plural = 'ofn'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
