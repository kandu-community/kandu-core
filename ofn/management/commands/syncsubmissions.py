# coding:utf-8

import os
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

import forms.models
from forms.misc import config_update_wrapper

class Command(BaseCommand):
    help = 'Synchronize submissions with a remote OFN instance'

    def add_arguments(self, parser):
        parser.add_argument('form_name', nargs=1)
        parser.add_argument('ofn_url', nargs=1)

    def handle(self, *args, **options):
        form_name, ofn_url = args

        model = getattr(forms.models, form_name)
        submissions = model.objects.all().order_by('-created_at')

        for submission in submissions:
            user = submission.baseformmodel_ptr.user
            
            # Do stuff here with submission and user.profile.ofn_token
            print submission, user
