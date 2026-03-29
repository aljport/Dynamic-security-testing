from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import *
from .models import *
from rest_framework.response import Response

# Create your views here.

class WebsiteViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def list(self, request):
        queryset = Website.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
