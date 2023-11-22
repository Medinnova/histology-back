from django.forms import CharField, DateTimeField
from rest_framework import serializers
from .models import Category
from users.serializers import UserField


class SectionField(serializers.RelatedField):
    queryset = Category.objects.all()
    def to_representation(self, value):
        return value.uuid
    def to_internal_value(self, data):
        try:
            return Category.objects.get(uuid=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )


class SectionSerializer(serializers.ModelSerializer):
    parent = SectionField(many=False, read_only=False, required=False)
    owners = UserField(many=True, read_only=False, required=False)
    name = CharField(max_length=200, min_length=1)
    class Meta:
        model = Category
        fields = ['id', 'uuid', 'name', 'parent', 'owners', 'created_at']