from rest_framework import serializers
from .models import Orders, OrderItem

class OrdersSerializer(serializers.ModelSerializer):
    """
    Serializer for the Orders model.

    This serializer converts the Orders model instances into JSON format and vice versa.
    It includes all fields from the Orders model.
    """
    class Meta:
        model = Orders
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.

    This serializer handles the conversion of OrderItem model instances to and from JSON.
    It includes all fields from the OrderItem model.
    """
    class Meta:
        model = OrderItem
        fields = '__all__'


class TopProductSerializer(serializers.Serializer):
    """
    Serializer for representing top product details.

    This serializer is used to structure the data for top products, including details
    like product name, pricing, quantity, and total orders.
    """
    product_name = serializers.CharField(source='item__product_name')
    is_discount = serializers.BooleanField(source='item__is_discount')
    price_after_discount = serializers.DecimalField(source='item__price_after_discount', max_digits=10, decimal_places=2)
    price = serializers.DecimalField(source='item__price', max_digits=10, decimal_places=2,)
    quantity = serializers.IntegerField()
    order = serializers.IntegerField()  
    total_orders = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_id = serializers.IntegerField(source='item__id')

    class Meta:
        fields = ['product_name', 'price', 'price_after_discount', 'is_discount', 'quantity', 'order', 'total_orders', 'total_price', "product_id"]


class CartSerializer(serializers.Serializer):
    """
    Serializer for representing cart items.

    This serializer structures the data related to items in a shopping cart,
    including product details such as name, price, discounts, quantity, and attributes.
    """
    id = serializers.IntegerField()
    product_name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_after_discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_discount = serializers.BooleanField()
    quantity = serializers.IntegerField()
    size = serializers.IntegerField()
    color = serializers.CharField()


class CreateOrdersSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders.

    This serializer is used to validate and save new Orders instances. It includes
    user information, address, receiver details, and gift cart status. Default
    values for send status and pay status are set during creation.
    """
    class Meta:
        model = Orders
        fields = ['user', 'address', 'receiver', 'gift_cart']  # Include the necessary fields
    
    def create(self, validated_data):
        """
        Create a new order instance with the provided validated data.

        This method sets default values for send status and pay status if they are not
        included in the validated data. It then saves the order instance to the database.

        Args:
            validated_data (dict): The validated data for creating the order.

        Returns:
            Orders: The created order instance.
        """
        validated_data.setdefault('send_status', 'p')  
        validated_data.setdefault('pay_status', 'progressing')  
        
        # Create the order instance
        order = Orders(**validated_data)
        order.save()
        return order