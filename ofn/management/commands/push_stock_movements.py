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

from forms.models import Stock_Movement
from forms.misc import config_update_wrapper

from ofn.models import Product


class Command(BaseCommand):
    help = 'Push stock movements to OFN'

    def api_endpoint(self, path):
        return settings.OFN['url'] + '/api/' + path

    def push_stock_movements(self, user):
        headers = { 'X-Spree-Token': user.profile.token }

        # sm = Stock_Movement.objects.create(user=user, Product="Potatoes", Quantity=10)
        # sm.save()

        stock_movements = Stock_Movement.objects.filter(user=user)

        for stock_movement in stock_movements:
            product = user.product_set.filter(name=stock_movement.Product).first()
            # variant_endpoint = self.api_endpoint('products/%s/variants/1' % product.remote_id)
            variant_endpoint = self.api_endpoint('products/6/variants/56')

            result = requests.get(variant_endpoint, headers=headers)
            spree_variant = result.json()
            print spree_variant

            data = {
                'variant[count_on_hand]': spree_variant['count_on_hand'] + stock_movement.Quantity
            }

            result = requests.put(variant_endpoint, headers=headers, data=data)
            print result.json()
            raise Exception('yo')

    def handle(self, *args, **options):
        for user in User.objects.all():
            if user.profile.token:
                self.push_stock_movements(user)
