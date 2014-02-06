from django.db.models import Model

class FormModel(Model):
	class Meta:
		abstract = True

	def model_name(self):
		return self.__class__.__name__

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()