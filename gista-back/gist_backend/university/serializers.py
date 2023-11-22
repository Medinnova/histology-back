from rest_framework import serializers
from users.models import User
from university.models import University

class UniversityField(serializers.RelatedField):
    queryset = University.objects.all()
    def to_representation(self, value):
        return value.id
    def to_internal_value(self, data):
        try:
            return University.objects.get(id=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )


class UniversitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, min_length=1)
    address = serializers.CharField(max_length=500, min_length=5)
