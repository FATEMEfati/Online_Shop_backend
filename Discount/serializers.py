from rest_framework import serializers
from .models import Gift_cart, Discount

class GiftCartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Gift_cart model.

    This serializer handles the serialization and deserialization
    of Gift_cart instances, allowing for easy conversion to and from
    JSON format. It includes all fields of the Gift_cart model.
    """

    class Meta:
        model = Gift_cart
        fields = '__all__'  

class DiscountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Discount model.

    This serializer facilitates the serialization and deserialization
    of Discount instances, enabling smooth conversion to and from
    JSON format. It includes all fields of the Discount model.
    """

    class Meta:
        model = Discount
        fields = '__all__'  