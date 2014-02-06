from django.db.models import Model, ForeignKey
from django.contrib.auth.models import User

class FormModel(Model):
	class Meta:
		abstract = True

	user = ForeignKey(User, editable=False)

	def model_name(self):
		return self.__class__.__name__

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()