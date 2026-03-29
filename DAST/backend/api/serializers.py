from rest_framework import serializers
from .models import *

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('id', 'name', 'url', 'scanned')
    