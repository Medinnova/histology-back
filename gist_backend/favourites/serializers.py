from rest_framework import serializers
from favourites.models import Favourite
from users.serializers import UserField
from gist.serializers import GistField

class FavouriteSerializer(serializers.Serializer):
    user = UserField(many=False, read_only=False, required=False)
    gist = GistField(many=False, read_only=False, required=False)


class FavouriteField(serializers.RelatedField):
    queryset = Favourite.objects.all()
    def to_representation(self, value):
        return value.id
    def to_internal_value(self, data):
        try:
            return Favourite.objects.get(id=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )