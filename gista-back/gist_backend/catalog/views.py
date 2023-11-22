from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SectionSerializer
from .models import Category
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from rest_framework import viewsets

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.http import Http404, JsonResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import AccessToken
from users.models import User

import json

from catalog.functions import get_sections, is_category_exists_at_same_level

from gist_backend.settings import MAX_SECTIONS

# Create your views here.
class GetSectionsAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
        operation_description='Получить секции для текущего пользователя',                
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        "sections": [
                            {
                                "id": '1',
                                "name": 'Общая гистология',
                                "subsections": [
                                    {
                                        "id": '2',
                                        "name": 'Мышечная ткань',
                                        "gists": [
                                            {
                                                "id": '3',
                                                "name": 'Название препарата',
                                                "img": 'some url'
                                            },
                                            {
                                                "id": '4',
                                                "name": 'Название препарата',
                                                "img": 'some url'
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": '5',
                                "name": 'Частная гистология',
                                "subsections": [  
                                    {
                                        "id": '2',
                                        "name": 'Мышечная ткань',
                                        "gists": [
                                            
                                        ]
                                    } 
                                ]
                            }
                        ]                                       
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Неверный токен!'                      
                    },                    
                }
            ),            
        })
    def get(self, request):   
        user = None
        token = None      

        try:
            token = request.META['HTTP_AUTHORIZATION']    
            token = token.split(" ")[1]  
        except Exception as e:
            print(e, token) 
            return Response({"error": "Missing header: Authorization"}, status=401)

        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])            
        except:
            return Response({"error": "User with given token not found!!"}, status=401)            

        sections = get_sections(user)
        
        return Response({
            'sections': sections,            
        })


class SectionViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["name", "parent", "owners"]
    http_method_names = ['get', 'head', 'patch', 'delete']
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = SectionSerializer

    def retrieve(self, request, pk=None):
        queryset = Category.objects.all()
        try:
            user = Category.objects.get(uuid=pk)
            serializer = SectionSerializer(user)
            return Response(serializer.data)
        except:
            raise Http404
    
    def get_object(self):
        uuid = self.kwargs.get('pk')
        return Category.objects.get(uuid=uuid)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

    # Дополнительно, если вам нужно переопределить метод perform_destroy:
    def perform_destroy(self, instance):
        instance.delete()

    
    # def get_queryset(self):
    #     sections_list = self.queryset.filter(parent_id__isnull=True).values()
    #     sections = []
    #     # Формирование json для разделов (sections)
    #     for i in sections_list:
    #         sections.append({
    #             'id': i['uuid'],
    #             'name': i['name']
    #         })

    #     subsections_list = self.queryset.filter(parent_id__isnull=False).values()
    #     subsections = []
    #     # Формирование json для подразделов (subsections)
    #     for i in subsections_list:
    #         subsections.append({
    #             'id': i['uuid'],
    #             'name': i['name'],
    #             'parent_id': i['parent_id']
    #         })
    #     return Response({
    #         'sections': sections,
    #         'subsections': subsections
    #     })
    


class CreateSectionView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Создать секцию для университета',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['section_id', 'name'],
            properties={
                'section_id': openapi.Schema(type=openapi.TYPE_STRING),                
                'name': openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(   
                description='',                    
                examples={
                    "application/json": {                                                
                        'message':'Some message'
                    },                    
                }
            ),   
            "401": openapi.Response(     
                description='',                  
                examples={
                    "application/json": {                                                
                        'error':'Some error'
                    },                    
                }
            ),            
        })
    def post(self, request):
        data = json.loads(request.body)
        name = data.get('name', '')
        section_id = data.get('section_id', None)   
        is_top = section_id is None
        token = None      
        section = None
        try:
            token = request.META['HTTP_AUTHORIZATION']            
            token = token.split(" ")[1]  
        except Exception as e:
            print(e, token)
            return Response({"error": "Missing header: Authorization"}, status=401)
        
        if len(name) == 0:
            return Response({"error": "Имя не должно быть пустым!"}, status=409)

        if len(name) > 1000:
            return Response({"error": "Имя слишком длинное!"}, status=409)

        if not is_top:
            try:
                section = Category.objects.get(uuid=section_id)  
            except:
                pass
        
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])

        if not user:
            return Response({"error": "No user found with given token"}, status=401)          

        user_sections = Category.objects.filter(owners__id=user.id)
        current_section_amount = user_sections.count()
        if current_section_amount >= MAX_SECTIONS:
            return Response({"error": "Создано максимальное количество разделов!"}, status=409)
        
        if is_category_exists_at_same_level(name, user, section):
            return Response({"error": "Раздел с таким именем уже существует!"}, status=409)

        new_section = Category.objects.create(name=name, parent=section)        
        new_section.owners.add(user)
        new_section.save()        
        return Response({'message': 'Все ок'}, status=200)