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

from users.views import get_current_user
# TODO надо будет сделать роли для конкретных гист, 
# чтобы одни люди кто имеет доступ к этой гисте
# могли что=то с ней делать в другие нет
# Например студент, которому не разрешил препод не может менять гисту
class GistViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["name", 'section']
    http_method_names = ['get', 'patch', 'delete']
    permission_classes = (IsAuthenticated,)
    queryset = Gist.objects.all()
    serializer_class = GistSerializer

    def retrieve(self, request, pk=None):
        user = get_current_user(request)
        if not user:
            return Response({"error": "Wrong access token"}, status=401)  

        queryset = Gist.objects.all()
        try:
            gist = Gist.objects.get(uuid=pk)
            if not gist.section.owners.contains(user):
                return Response({"error": "Нет прав для просмотра этой гисты!"}, status=status.HTTP_409_CONFLICT)  

            serializer = GistSerializer(gist)
            return Response(serializer.data)
        except:
            raise Http404
        
    def partial_update(self, request, pk=None):
        queryset = Gist.objects.all()
        try:
            gist = queryset.get(uuid=pk)
        except Gist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = get_current_user(request)
        if not user:
            return Response({"error": "Wrong access token"}, status=401)
        
        if not gist.section.owners.contains(user):
            return Response({"error": "Нет прав для изменения этой гисты!"}, status=status.HTTP_409_CONFLICT)  

        serializer = GistSerializer(gist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        queryset = Gist.objects.all()
        try:
            gist = queryset.get(uuid=pk)            
        except Gist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = get_current_user(request)
        if not user:
            return Response({"error": "Wrong access token"}, status=401)
        
        if not gist.section.owners.contains(user):
            return Response({"error": "Нет прав для удаления этой гисты!"}, status=status.HTTP_409_CONFLICT)  

        gist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)