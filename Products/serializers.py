from rest_framework import serializers
from .models import Product, Category, ProductAttribute, Gallery, Diversity

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    This serializer handles the serialization and deserialization of 
    Product instances, allowing for easy conversion to and from JSON 
    representations.
    """
    class Meta:
        model = Product
        fields = '__all__'  

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    This serializer provides a way to serialize and deserialize 
    Category instances, facilitating the conversion to and from JSON 
    format for API interactions.
    """
    class Meta:
        model = Category
        fields = '__all__'  

class DiversitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Diversity model.

    This serializer manages the serialization and deserialization 
    of Diversity instances, enabling their conversion to and from 
    JSON representations for use in APIs.
    """
    class Meta:
        model = Diversity
        fields = '__all__' 

class ProductAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductAttribute model.

    This serializer is responsible for converting ProductAttribute 
    instances to and from JSON format, allowing for seamless 
    integration with API endpoints.
    """
    class Meta:
        model = ProductAttribute
        fields = '__all__' 

class GallerySerializer(serializers.ModelSerializer):
    """
    Serializer for the Gallery model.

    This serializer handles the serialization and deserialization 
    of Gallery instances, making it easy to convert them to and 
    from JSON representations for API communication.
    """
    class Meta:
        model = Gallery
        fields = '__all__' 