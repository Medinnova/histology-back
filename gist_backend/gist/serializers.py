from rest_framework import serializers
from django.forms import CharField

from .models import Gist
from catalog.models import Category
from catalog.serializers import SectionField

class GistSerializer(serializers.ModelSerializer):
    section = SectionField(many=False, read_only=False, required=True)
    image = serializers.FileField(max_length=1000, use_url=True, allow_null=False, required=True)
    dzi_image = serializers.FileField(max_length=1000, use_url=True, allow_null=True, read_only=True)
    crop_image = serializers.FileField(max_length=1000, use_url=True, allow_null=True, read_only=True)
    marking = serializers.CharField(required=False)
    class Meta:
        model = Category
        fields = ['id', 'uuid', 'name', 'section', 'image', 'dzi_image', 'crop_image','marking']
    

class GistField(serializers.RelatedField):
    queryset = Gist.objects.all()
    def to_representation(self, value):
        return value.uuid
    def to_internal_value(self, data):
        try:
            return Gist.objects.get(uuid=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )