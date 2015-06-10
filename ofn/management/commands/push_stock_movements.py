# coding:utf-8

import json
import os
import re
import requests
import iso8601

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

from forms.models import Stock
from forms.misc import config_update_wrapper

from ofn.models import Variant


class Command(BaseCommand):
    help = 'Push stock movements to OFN'

    def api_endpoint(self, path):
        return settings.OFN['url'] + '/api/' + path

    def push_stock_movements(self, user):
        headers = { 'X-Spree-Token': user.profile.token }

        # sm = Stock_Movement.objects.create(user=user, Product="Potatoes", Quantity=10)
        # sm.save()

        stock_movements = Stock.objects.filter(user=user)

        for stock_movement in stock_movements:
            # It's called Product, but it's actually a Variant.id
            variant_id = stock_movement.Product
            variant = Variant.objects.get(id=variant_id)

            variant_endpoint = self.api_endpoint('products/%s/variants/%s' % (variant.product.remote_id, variant.remote_id))

            result = requests.get(variant_endpoint, headers=headers)
            before = result.json()

            data = {
                'variant[count_on_hand]': before['count_on_hand'] + stock_movement.Quantity
            }

            result = requests.put(variant_endpoint, headers=headers, data=data)
            after = result.json()

            print "%s - %s : %s -> %s" % (variant.product, variant, before['count_on_hand'], after['count_on_hand'])

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.profile.token:
                self.push_stock_movements(user)
