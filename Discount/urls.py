from django.urls import path
from .views import GiftCartList

urlpatterns = [
    path('api-v1/gift cart/', GiftCartList.as_view(), name='gift-cart-list'),
]