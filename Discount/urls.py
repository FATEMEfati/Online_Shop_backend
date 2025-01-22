from django.urls import path
from .views import GiftCartList

urlpatterns = [
    path('api-v1/gift_cart/', GiftCartList.as_view(), name='gift-cart-list'),
]