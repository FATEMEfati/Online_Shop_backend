from django.urls import path
from .views import (OrderItemList,OrdersList,TopProduct,TopCategory,
                    AddToCart,Delete,RemoveFromCart,TotalPrice,
                    ShowCart,NumberOfProduct,OrderCreateView,DeleteOrder)

urlpatterns = [
    path('api-v1/orders/<int:user_id>', OrdersList.as_view(), name='orders-list'),
    path('api-v1/orderItem/<int:order_id>', OrderItemList.as_view(), name='orderitem-list'),
    path('api-v1/delete_order/<int:order_id>', DeleteOrder.as_view(), name='delete_order'),
    path('api-v1/top_product/', TopProduct.as_view(), name='top_product'),
    path('api-v1/top_categories/', TopCategory.as_view(), name='top_category'),
    path('api-v1/add_to_cart/', AddToCart.as_view(), name='add_to_cart'),
    path('api-v1/remove_from_cart/', RemoveFromCart.as_view(), name='remove_from_cart'),
    path('api-v1/delete_from_cart/', Delete.as_view(), name='delete_from_cart'),
    path('api-v1/total_price/', TotalPrice.as_view(), name='total_price'),
    path('api-v1/show_cart/', ShowCart.as_view(), name='show_cart'),
    path('api-v1/number_of_product/', NumberOfProduct.as_view(), name='number_of_product'),
    path('api-v1/create_order/', OrderCreateView.as_view(), name='order-create'),
]