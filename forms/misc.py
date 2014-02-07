from django.db.models import Model, ForeignKey
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager

class BaseFormModel(Model):
	user = ForeignKey(User, editable=False)

	objects = InheritanceManager()

	def model_name(self):
		return self.__class__.__name__

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()