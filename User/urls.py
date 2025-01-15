from django.urls import path
from .views import (UserList,CommentList,AddressList,LoginView,
                    UserCreateView,GenerateCodeView,ValidateCodeView,TokenInfoView,
                    UserInfo,UpdateUserInfo,UserUpdatePassView,AddressListPost,HeroGalleryView)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


urlpatterns = [
    path('api-v1/users/', UserList.as_view(), name='user-list'),
    path('api-v1/login', LoginView.as_view(), name='login'),
    path('api-v1/comments/', CommentList.as_view(), name='comment-list'),
    path('api-v1/address_for_user/<int:user_id>', AddressList.as_view(), name='address-list'),
    path('api-v1/create_address_for_user/', AddressListPost.as_view(), name='address-list_post'),
    path('api-v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api-v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-v1/register_users/', UserCreateView.as_view(), name='user-create'),
    path('api-v1/generate-code/', GenerateCodeView.as_view(), name='generate_code'),
    path('api-v1/validate-code/', ValidateCodeView.as_view(), name='validate_code'),
    path('api-v1/token_info/', TokenInfoView.as_view(), name='token_info'),
    path('api-v1/user_info/<int:user_id>', UserInfo.as_view(), name='user-info'),
    path('api-v1/update_user_info/<int:user_id>', UpdateUserInfo.as_view(), name='update_user-info'),
    path('api-v1/update_user_pass/<int:user_id>', UserUpdatePassView.as_view(), name='update_user_pass-info'),
    path('api-v1/herogallery/', HeroGalleryView.as_view(), name='hero_gallery'),
    
]

