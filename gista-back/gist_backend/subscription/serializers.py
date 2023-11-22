from rest_framework import serializers
from users.models import User
from subscription.models import Subscription, Plan


class PlanField(serializers.RelatedField):
    queryset = Plan.objects.all()
    def to_representation(self, value):
        return value.name
    def to_internal_value(self, data):
        try:
            return Plan.objects.get(name=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )
            

class SubscriptionField(serializers.RelatedField):
    queryset = Subscription.objects.all()
    def to_representation(self, value):
        return value.id
    def to_internal_value(self, data):
        try:
            return Subscription.objects.get(id=data)
        except KeyError:
            raise serializers.ValidationError(
                'id is a required field.'
            )
        except ValueError:
            raise serializers.ValidationError(
                'id must be an integer.'
            )


class SubscriptionSerializer(serializers.Serializer):
    plan = PlanField(many=False, read_only=False, required=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
