from rest_framework import serializers
from .models import User
from university.serializers import UniversityField
from subscription.serializers import SubscriptionSerializer
from rolepermissions.roles import get_user_roles
from django.contrib.auth.models import Permission

class UserSerializer(serializers.ModelSerializer):
    university = UniversityField(many=False, read_only=False, required=False)
    subscription = SubscriptionSerializer(many=False, read_only=False, required=False)
    role = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'university', 'subscription', 'first_name', 'surname', 'last_name', 'phone_number', 'role', 'permissions']

    def get_role(self, obj):
        roles = get_user_roles(obj)
        return roles[0].get_name() if roles else None
    
    def get_permissions(self, obj):
        roles = get_user_roles(obj)
        if not roles:
            return []
        permissions = [x.codename for x in Permission.objects.filter(user=obj)]        
        return permissions

class UserField(serializers.RelatedField):
    queryset = User.objects.all()
    def to_representation(self, value):
        return value.id
    def to_internal_value(self, data):
        try:
            return User.objects.get(id=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )
