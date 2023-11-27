from rest_framework.views import APIView
from rest_framework.response import Response

from gist_backend.settings import EMAIL_HOST_USER
from .serializers import UserSerializer
from .models import User, Confirmation
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from gist.models import Gist
from catalog.models import Category
from favourites.models import Favourite
from django.core.mail import send_mail

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from rolepermissions.roles import assign_role

import re

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.http import Http404
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import AccessToken

import json

from django.db.models import Q


class UserViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["first_name", "last_name", 'surname', 'phone_number', 'university', 'subscription']
    http_method_names = ['get', 'post', 'head', 'patch']
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, token=None):
        queryset = User.objects.all()
        try:            
            access_token = AccessToken(token)
            user = User.objects.get(access_token['user_id'])
            # user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except:
            raise Http404


class UserGists(APIView):
    @swagger_auto_schema(
        operation_description='Гисты пользователя',        
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "sections": [
                            {
                                'name': 'Общая гистология',
                                'gists': [
                                    {
                                        'name': 'Мазок бла бла',
                                        'preview_image': 'url',
                                        'university': 'UNIVER_NAME'
                                    },
                                    {
                                        'name': 'Мазок бла бла',
                                        'preview_image': 'url',
                                        'university': 'UNIVER_NAME'
                                    }
                                ],
                            },
                            {
                                'name': 'Частная гистология',
                                'subsections': [
                                    {
                                        'name': 'Subsection1',
                                        'gists': [
                                            {
                                                'name': 'Мазок бла бла',
                                                'preview_image': 'url',
                                                'university': 'UNIVER_NAME'
                                            },
                                            {
                                                'name': 'Мазок бла бла',
                                                'preview_image': 'url',
                                                'university': 'UNIVER_NAME'
                                            }
                                        ],
                                    },
                                    {
                                        'name': 'Subsection2',
                                        'gists': [
                                            {
                                                'name': 'Мазок бла бла',
                                                'preview_image': 'url',
                                                'university': 'UNIVER_NAME'
                                            },
                                            {
                                                'name': 'Мазок бла бла',
                                                'preview_image': 'url',
                                                'university': 'UNIVER_NAME'
                                            }
                                        ],
                                    },
                                ]
                            },
                        ],                                                
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Wrong Token'                      
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
        except:
            return Response({"error": "Missing parameter: token"}, status=401)
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            # user = User.objects.get(id=user_id)
        except:
            return Response({"error": "Wrong ID"}, status=404)
        
        response = {
            'sections': []
        }

        sections_types = ['free', 'all']
        main_sections = [item for item in Category.objects.filter(code_name__in=sections_types)]

        private_section = Category.objects.get(code_name='private')
        
        for main_section in main_sections:
            current_gists = Gist.objects.filter(section=main_section)
            response['sections'].append({
                "name": main_section.name,
                "gists": [item.to_json() for item in current_gists]
            })
        
        sub_sections = Category.objects.filter(parent_id=private_section.id)
        response['sections'].append({
            "name": private_section.name,
            "subsections": []            
        })
        
        for subsection in sub_sections:
            current_gists = Gist.objects.filter(section=subsection)
            response['sections'][2]['subsections'].append({
                "name": subsection.name,
                "gists": [item.to_json() for item in current_gists]            
            })      

        return Response(response, status=200)    
        

class UsersAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Авторизация',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username','password'],
            properties={
                'username':openapi.Schema(type=openapi.TYPE_STRING),
                'password':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        'access': "TOKEN",
                        "user": {"some field": 'data'},
                        'is_staff': True                      
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Неверный логин или пароль!'                      
                    },                    
                }
            ),            
        })
    def post(self, request):
        username = request.data['username']
        unhashed_pass = request.data['password']
        # Check username exists
        if not User.objects.filter(username=username).exists():
            return Response({'success': False,
                             'message': 'Неверное имя пользователя или пароль'}, status=200)
        self.user = User.objects.get(username=username)
        serializer = UserSerializer(self.user)
        data = serializer.data
        data.pop("password", None)
        hashed_pass = self.user.password
        if check_password(unhashed_pass, hashed_pass):
            refresh = RefreshToken.for_user(self.user)
            res = {
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                "user": data,
                'is_staff': self.user.is_staff
            }
            response = Response(res, status=200)
            response.set_cookie(
                key='refresh',
                value=refresh,
                expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                httponly=True,
                samesite="None",
                secure=True
            )
            response.set_cookie(
                key='user_id',
                value=self.user.id,
                httponly=True,
                samesite="None",
                secure=True
            )
            return response
        else:
            return Response({'success': False,
                             'message': 'Неверное имя пользователя или пароль'}, status=200)


class UserGetAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Получить юзера по токену',                
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        'user': {
                            "some_data": 'data'
                        },                                        
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
        token = request.META['HTTP_AUTHORIZATION']                
        token = token.split(" ")[1] 
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])            
            serializer = UserSerializer(user)
            data = serializer.data
            data.pop("password", None)
            return Response({"success": True, "user": data})
        except Exception as e:
            print(e)
            return Response({"success": False})


class RegisterAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Регистрация',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email','phone'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING),
                'phone':openapi.Schema(type=openapi.TYPE_STRING),
                'password':openapi.Schema(type=openapi.TYPE_STRING),
                'first_name':openapi.Schema(type=openapi.TYPE_STRING),
                'last_name':openapi.Schema(type=openapi.TYPE_STRING),
                'surname':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "success": True,  
                        'message': 'Пользователь успешно создан!'                      
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Такой пользователь уже существует!'                      
                    },                    
                }
            ),            
        })
    def post(self, request):
        unhashed_pass = request.data['password']
        
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        surname = request.data['surname']

        for e in first_name + last_name + surname:
            if not e.isalnum():
                return Response({'success': False, 'message': 'ФИО не должно содержать специальных символов!'}, status=401) 
        
        email = request.data['email']
        phone = request.data['phone']
        replace_list = ['(', ')', '-', '+', ' ']
        for symbol in replace_list:
            phone = phone.replace(symbol, '')

        try:
            User.objects.get(email=email)
            User.objects.get(phone=phone)
            return Response({'success': False, 'message': 'Такой пользователь уже существует!'}, status=401)
        except:
            pass
        
        new_user = User.objects.create(username=email, first_name=first_name, last_name=last_name, surname=surname, email=email, phone_number=phone)
        new_user.set_password(unhashed_pass)
        assign_role(new_user, 'default')
        new_user.save()

        # public_section = Category.objects.get(code_name=PUBLIC_SECTION_CODE_NAME)
        public_section = Category.objects.create(name="Общая гистология")
        public_section.owners.add(new_user)
        public_section.save()

        private_section = Category.objects.create(name="Частная гистология")
        private_section.owners.add(new_user)
        private_section.save()
        
        return Response({'success': True, 'message': 'Пользователь успешно создан!'}, status=200)
        

class UserExistsAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Существует ли пользователь',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email','phone'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING),
                'phone':openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            "200": openapi.Response(         
                description='',       
                examples={
                    "application/json": {
                        "exists": True,                        
                    },                    
                }
            ),            
        })
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', '')
        phone = data.get('phone', '')        
        phone = re.sub('[()+-]', '', phone)
        
        
        users = User.objects.filter(Q(phone_number=phone) | Q(email=email))    
        if users:        
            return Response({'exists': True}, status=200)
        else:
            return Response({'exists': False}, status=200)
        


class SendRestoreLinkAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Отправить ссылку для восстановления пароля',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(         
                description='',       
                examples={
                    "application/json": {
                        'success': True,                        
                        'message':'some message'
                    },                    
                }
            ),
            "401": openapi.Response(  
                description='',                     
                examples={
                    "application/json": {
                        'success': False,                        
                        'message':'some error'
                    },                    
                }
            ),            
        })
    def post(self, request):        
        email = request.data['email']
        
        try:
            User.objects.get(email=email)
        except:
            return Response({'success': False, 'message': 'Такой пользователь не существует!'}, status=401)
        
        # TODO Придумать в каком виде отправлять ссылку для восстановления пароля
        link = "SOME LINK"
        html_message = render_to_string('reset_password.html', {'link': link})
        plain_message = strip_tags(html_message)
        send_mail(
            "Восстановление пароля",
            plain_message,
            EMAIL_HOST_USER,
            [email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({'success': True, 'message': 'Ссылка для восстановления пароля была отправлена на ваш email!'}, status=200)


class SendConfirmationCodeAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Отправить код на почту',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),
        responses={
            "200": openapi.Response(                
                description='',       
                examples={
                    "application/json": {
                        'success': True,
                        'code': "234763",
                        'message':'Код для подтверждения почты был отправлен на ваш email!'
                    },                    
                }
            ),
            "401": openapi.Response(     
                description='',                  
                examples={
                    "application/json": {
                        'success': False,                        
                        'message':'Такой пользователь не существует!'
                    },                    
                }
            ),            
        })
    def post(self, request):        
        email = request.data['email']
        confirmation = None
        try:
            confirmation = Confirmation.objects.get(email=email)
        except:
            pass
        
        confirmation = Confirmation.objects.create(email=email)
        
        return Response({'success': True, 'code': confirmation.code, 'message': 'Код для подтверждения почты был отправлен на ваш email!'}, status=200)



class RestorePasswordAPIView(APIView):
    @swagger_auto_schema(
        operation_description='Изменить пароль на новый',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email':openapi.Schema(type=openapi.TYPE_STRING),                
                'password':openapi.Schema(type=openapi.TYPE_STRING),                            
            },
        ),
        responses={
            "200": openapi.Response(   
                description='',                    
                examples={
                    "application/json": {
                        'success': True,                        
                        'message':'Пароль успешно был изменен!'
                    },                    
                }
            ),
            "401": openapi.Response(   
                description='',                    
                examples={
                    "application/json": {
                        'success': False,                        
                        'message':'Такой пользователь не существует!'
                    },                    
                }
            ),            
        })
    def post(self, request):        
        password = request.data['password']
        email = request.data['email']
        
        user = None
        try:
            user = User.objects.get(email=email)
        except:
            return Response({'success': False, 'message': 'Такой пользователь не существует!'}, status=401)
        
        user.set_password(password)

        return Response({'success': True, 'message': 'Пароль успешно был изменен!'}, status=200)


class RefreshTokenView(APIView):
    def get(self, request):
        print(request.COOKIES)
        refresh = request.COOKIES.get('refresh')
        user_id = request.COOKIES.get('user_id')
        user = User.objects.get(id=user_id)
        ref = RefreshToken.for_user(user)
        res = {'access': str(ref.access_token)}
        response = Response(res)
        response.set_cookie(key='refresh', value=str(ref))
        return Response(
            {'access': str(ref.access_token)},
            status=200
        )


# Добавить\Удалить из избранного
class FavouriteView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Добавить/Удалить из избранного',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['gist_id', 'user_id'],
            properties={
                'gist_id':openapi.Schema(type=openapi.TYPE_INTEGER),                
                'user_id':openapi.Schema(type=openapi.TYPE_INTEGER),                            
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
        token = data.get("token")  
        gist_id = data.get('gist_id')
        current_user = None
        try:
            access_token = AccessToken(token)
            current_user = User.objects.get(id=access_token['user_id'])
        except:
            return Response({"error": "Unauthorized!"}, status=401)

        gist = None
        try:
            gist = Gist.objects.get(id=gist_id)
        except:
            return Response({"error": "Гиста с таким id не найдена!"}, status=401)
        
        # Если гиста добавлена в избранное - удаляем, не добавлена - добавляем
        try:
            favourite = Favourite.objects.get(user=current_user, gist=gist)
            favourite.delete()
        except:
            favourite = Favourite.objects.create(user=current_user, gist=gist)
            favourite.save()
        
        return Response({'message': 'Все ок'}, status=200)
    

class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description='Загрузить изображение от имени пользователя университета',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['image', 'name', 'section_id'],
            properties={
                'image': openapi.Schema(type=openapi.TYPE_FILE),                
                'name': openapi.Schema(type=openapi.TYPE_STRING),                
                'section_id': openapi.Schema(type=openapi.TYPE_STRING),                
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
        # data = json.loads(request.body)
        # name = data.get('name', '')
        # image = data.get('image', '')                   
        # section_id = data.get('section_id', '')

        image = request.FILES.get('image')
        name = request.POST.get('name')
        section_id = request.POST.get('section_id') 
                   
        token = None      
        try:
            token = request.META['HTTP_AUTHORIZATION']
            token = token.split(" ")[1]  
        except Exception as e:
            print(e, token) 
            return Response({"error": "Missing header: Authorization"}, status=401)
        
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id'])

        if not user:
            return Response({"error": "No user found with given token"}, status=401)           

        if len(name) == 0:
            return Response({"error": "Имя не должно быть пустым!"}, status=409)

        if len(name) > 1000:
            return Response({"error": "Имя слишком длинное!"}, status=409)

        section = None
        try:
            section = Category.objects.get(uuid=section_id)
        except:
            return Response({"error": "No section found with given id"}, status=409)        

        gist = Gist.objects.create(dzi_image=image, image=image, name=name, section=section)        
        gist.save()        
        return Response({'message': 'Все ок', "id": gist.uuid}, status=200)
    