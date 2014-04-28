from rest_framework import serializers

from models import Icon

class IconSerializer(serializers.ModelSerializer):
	class Meta:
		model = Icon
		exclude = ('icon_file',)

	icon_file_url = serializers.SerializerMethodField('instance_icon_file_url')

	def instance_icon_file_url(self, obj):
		return obj.icon_file.url