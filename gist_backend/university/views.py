from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import University, UniversityCode
from django.http import HttpResponse
from django.conf import settings
from rest_framework import authentication, exceptions
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# views

from rolepermissions.checkers import has_permission
from rolepermissions.roles import assign_role, get_user_roles, clear_roles

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.http import Http404, JsonResponse

from university.serializers import UniversitySerializer
from rest_framework import viewsets

from rest_framework_simplejwt.tokens import AccessToken

import json

class UniversityViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["name", "address"]
    http_method_names = ['get', 'post', 'head', 'patch']
    permission_classes = (IsAuthenticated,)
    queryset = University.objects.all()
    serializer_class = UniversitySerializer

    def retrieve(self, request, pk=None):
        queryset = University.objects.all()
        try:
            user = University.objects.get(id=pk)
            serializer = UniversitySerializer(user)
            return Response(serializer.data)
        except:
            raise Http404

# Подключение к универу через код
class ConnectUniversity(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Подключиться к универу по коду',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        'message': "Some message",                                            
                    },                    
                }
            ),
            "400": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Some error'                      
                    },                    
                }
            ),            
        })
    def post(self, request):
        token = None
        try:
            token = request.META['HTTP_AUTHORIZATION']
            token = token.split(" ")[1]  
        except Exception as e:
            print(e, token)
            return Response({"error": "Missing header: Authorization"}, status=401)
        
        access_token = AccessToken(token)
        current_user = User.objects.get(id=access_token['user_id'])

        if not current_user:
            return Response({"error": "No user found with given token"}, status=401)

        data = json.loads(request.body)
        code = data.get('code', '')
        requested_university = None
        try:
            code_model = UniversityCode.objects.get(code=code)
            requested_university = code_model.university
        except:
            return Response({"error": "Такой код не найден!"}, status=401)

        current_user.university = requested_university
        current_user.save()
        code_model.delete()
        clear_roles(current_user)
        assign_role(current_user, 'student')
        
        return Response({'message': 'Вы успешно подключили университет!'}, status=200)


class GenerateCodes(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Сгенерировать коды для универа',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['university_id','amount'],
            properties={
                'university_id': openapi.Schema(type=openapi.TYPE_STRING),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER),                
            },
        ),
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        'message': "Some message",                                            
                    },                    
                }
            ),
            "400": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Some error'                      
                    },                    
                }
            ),            
        })
    def post(self, request):        
        university_id = request.data['university_id']
        amount = request.data["amount"]
        university = None

        try:
            university = University.objects.get(id=university_id)
        except:
            return Response({"error": "University not found!"}, status=400)            

        i = 0
        while i < amount:
            current_code = UniversityCode.objects.create(university=university)
            current_code.save()
            i+=1
        
        return Response({'message': 'Коды успешно созданы!'}, status=200)

