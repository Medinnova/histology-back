from django.shortcuts import render
from favourites.models import Favourite
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from favourites.serializers import FavouriteSerializer
from rest_framework import viewsets


class FavouriteViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["user", "gist"]
    http_method_names = ['get', 'delete']
    permission_classes = (IsAuthenticated,)
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer

    def retrieve(self, request, pk=None):
        queryset = Favourite.objects.all()
        try:
            user = Favourite.objects.get(id=pk)
            serializer = FavouriteSerializer(user)
            return Response(serializer.data)
        except:
            raise Http404