from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GistSerializer
from .models import Gist
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from django.http import Http404, JsonResponse

class GistViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["name", 'section']
    http_method_names = ['get', 'head', 'patch', 'delete']
    permission_classes = (IsAuthenticated,)
    queryset = Gist.objects.all()
    serializer_class = GistSerializer

    def retrieve(self, request, pk=None):
        queryset = Gist.objects.all()
        try:
            user = Gist.objects.get(uuid=pk)
            serializer = GistSerializer(user)
            return Response(serializer.data)
        except:
            raise Http404
        
    def partial_update(self, request, pk=None):
        queryset = Gist.objects.all()
        try:
            gist = queryset.get(uuid=pk)
        except Gist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = GistSerializer(gist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # TODO
    # В будущем нужно будет проверять права доступа пользователя
    def destroy(self, request, pk=None):
        queryset = Gist.objects.all()
        try:
            gist = queryset.get(uuid=pk)
        except Gist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        gist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)