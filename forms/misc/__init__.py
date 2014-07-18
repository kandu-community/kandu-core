from functions import config_update_wrapper


from django.db.models import Model, ForeignKey, DateTimeField
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.gis.db.models import PointField
from model_utils.managers import InheritanceManager
from django.core.urlresolvers import reverse


class BaseFormModel(Model):
	user = ForeignKey(User, related_name='user')
	created_at = DateTimeField(auto_now_add=True)

	objects = InheritanceManager()

	show_on_map = False
	is_editable = False
	is_creatable = True
	inlines = None

	def model_name(self):
		return self.__class__.__name__

	def get_absolute_url(self):
		return reverse('web_update', kwargs={'model_name': self.model_name(), 'pk': self.pk})

	@classmethod
	def location_field(cls):
		try:
			field_name = next( field.name for field in cls._meta.fields if isinstance(field, PointField) )
		except StopIteration:
			return None
		return field_name

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()

	def __unicode__(self):
		try:
			return u', '.join( unicode(getattr(self, field_name)) for field_name in self.label_fields if hasattr(self, field_name) and getattr(self, field_name) != None )
		except AttributeError:
			return self.__class__.verbose_name()

@receiver(signals.post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
	if created:
		group, created = Group.objects.get_or_create(name='basic')
		group.user_set.add(instance)
		group.save()