from rest_framework import serializers

from forms.misc import BaseFormModel

class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseFormModel