from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Subscription, Plan
from django.http import HttpResponse
from django.conf import settings
from rest_framework import authentication, exceptions
from users.models import User
from dateutil.relativedelta import relativedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from subscription.serializers import SubscriptionSerializer

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.http import Http404, JsonResponse
from rest_framework import viewsets


class SubscriptionViewSet(viewsets.ModelViewSet):
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_fields = ["plan", "start_date", 'end_date', 'is_active']
    http_method_names = ['get', 'post', 'head', 'patch']
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def retrieve(self, request, pk=None):
        queryset = Subscription.objects.all()
        try:
            user = Subscription.objects.get(id=pk)
            serializer = SubscriptionSerializer(user)
            return Response(serializer.data)
        except:
            raise Http404

# Оформить подписку
class BuySubscrition(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    @swagger_auto_schema(
        operation_description='Купить подписку',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id','subscription_plan_id'],
            properties={
                'user_id':openapi.Schema(type=openapi.TYPE_STRING),
                'subscription_plan_id':openapi.Schema(type=openapi.TYPE_STRING),                
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
        user_id = request.data['user_id']
        current_user = None
        try:
            current_user = User.objects.get(id=user_id)
        except:
            return Response({"error": "Unauthorized!"}, status=400)            

        subscription_plan_id = request.data['subscription_plan_id']
        plan = None
        try:
            plan = Plan.objects.get(id=subscription_plan_id)
        except:
            return Response({"error": "Плана подписки с таким id не найдено!"}, status=400)

        current_user.subscription = Subscription.objects.create(plan=plan)
        current_user.save() 
        
        return Response({'message': 'Вы успешно приобрели подписку!'}, status=200)
    

# Продлить подписку
class RenewSubscrition(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    @swagger_auto_schema(
        operation_description='Продлить подписку',        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id','subscription_plan_id'],
            properties={
                'user_id':openapi.Schema(type=openapi.TYPE_STRING),                                
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
        user_id = request.data['user_id']
        current_user = None
        try:
            current_user = User.objects.get(id=user_id)
        except:
            return Response({"error": "Unauthorized!"}, status=400)            

        # TODO тут оплата и если успешно то продляем

        current_user.subscription.start_date = current_user.subscription.end_date
        current_user.subscription.end_date = current_user.subscription.end_date + relativedelta(months=current_user.subcription.duration)
        current_user.save() 
        
        return Response({'message': 'Вы успешно продлили подписку!'}, status=200)