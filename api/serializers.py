from rest_framework import serializers

from forms.misc import BaseFormModel

class BaseFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseFormModel

    form_class = serializers.SerializerMethodField('instance_model_name')

    def instance_model_name(self, obj):
    	return obj.model_name()