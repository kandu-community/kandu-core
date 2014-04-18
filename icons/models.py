import os
from django.db.models import Model, ForeignKey, ImageField, BooleanField

class Icon(Model):
	icon_file = ImageField(upload_to='icons')
	partner_icon = BooleanField(u'partner logo', default=True)

	def __unicode__(self):
		return os.path.split(self.icon_file.url)[-1]