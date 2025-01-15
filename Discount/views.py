from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Gift_cart
from .serializers import GiftCartSerializer
from rest_framework.permissions import IsAuthenticated
class GiftCartList(APIView):
    """
    API view to retrieve a list of gift carts.

    This view handles GET requests to retrieve all instances of the Gift_cart model.
    It serializes the data using the GiftCartSerializer and returns it in the response.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        """
        Handles GET requests to retrieve all gift carts.

        Args:
            request: The HTTP request object.
            format: Optional; the format of the response (e.g., JSON). Defaults to None.

        Returns:
            Response: A Response object containing a serialized list of gift carts.
        """
        data = Gift_cart.objects.all()
        serializer = GiftCartSerializer(data, many=True)
        return Response(serializer.data)