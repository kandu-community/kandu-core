from rest_framework import generics

from models import Icon
from serializers import IconSerializer

class IconList(generics.ListAPIView):
	model = Icon
	serializer_class = IconSerializer