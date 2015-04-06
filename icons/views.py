from rest_framework import generics

from models import Icon
from serializers import IconSerializer

class IconList(generics.ListAPIView):
	queryset = Icon.objects.all()
	serializer_class = IconSerializer