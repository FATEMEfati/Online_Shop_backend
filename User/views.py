from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User,Address, Comments,HeroGallery
from .serializers import (UserSerializer,AddressSerializer,CommentsSerializer,
                          UserRegisterSerializer,UserLoginSerializer,
                          TokenInfoSerializer,UserUpdateSerializer,
                          UserUpdatePassSerializer,HeroGallerySerializer)
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status,generics
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import UntypedToken
import random
import string
from datetime import timedelta
from datetime import timedelta
from django.utils import timezone
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from decimal import Decimal

class UserList(APIView):
    """API view to list all users."""

    def get(self, request, format=None):
        """
        Retrieve a list of all users.

        Args:
            request: The HTTP request object.
            format: The format of the response (optional).

        Returns:
            Response: A Response object containing user data.
        """
        data = User.objects.all()
        serializer = UserSerializer(data, many=True)
        return Response(serializer.data)


class CommentList(APIView):
    """API view to list all comments."""

    def get(self, request, format=None):
        """
        Retrieve a list of all comments.

        Args:
            request: The HTTP request object.
            format: The format of the response (optional).

        Returns:
            Response: A Response object containing comment data.
        """
        data = Comments.objects.all()
        serializer = CommentsSerializer(data, many=True)
        return Response(serializer.data)


class AddressList(APIView):
    """API view to manage user addresses."""
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        """
        Retrieve all addresses for a specific user.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user whose addresses to retrieve.

        Returns:
            Response: A Response object containing address data.
        """
        data = Address.objects.filter(user=user_id, is_delete=False)
        serializer = AddressSerializer(data, many=True)
        return Response(serializer.data)

    def put(self, request, user_id):
        """
        Update an existing address for a user.

        Args:
            request: The HTTP request object containing address data.
            user_id: The ID of the user whose address is to be updated.

        Returns:
            Response: A Response object with the status of the update.
        """
        address_id = request.data.get('id')
        try:
            address = Address.objects.get(id=address_id, user=user_id, is_delete=False)
        except Address.DoesNotExist:
            return Response({'message': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)

        postal_code = request.data.get('postal_code')
        if Address.objects.exclude(id=address_id).filter(postal_code=postal_code, user=str(Decimal(user_id))).exists():
            return Response({'message': 'Address with this postal code already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            updated_address = serializer.save()
            return Response({'id': updated_address.id, 'message': 'Address updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'message': 'There is a problem'}, status=status.HTTP_400_BAD_REQUEST)


class AddressListPost(APIView):
    """API view to create a new address."""
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Create a new address.

        Args:
            request: The HTTP request object containing address data.

        Returns:
            Response: A Response object with the status of the creation.
        """
        postal_code = request.data.get('postal_code')
        user_id= request.data.get('user')
        print(type(user_id))
        if Address.objects.exclude(is_delete=True).filter(postal_code=postal_code , user=user_id).exists():
            return Response({'message': 'Address with this postal code already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save()
            return Response({'id': address.id, 'message': 'Address created successfully.'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'There is a problem'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """API view to handle user login."""

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle user login and token generation.

        Args:
            request: The HTTP request object containing user credentials.

        Returns:
            Response: A Response object containing access and refresh tokens.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        # Create tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access.set_exp(lifetime=timedelta(hours=8))
        response = Response({
            'access': str(access),
            'refresh': str(refresh),
            'username': user.username,
            'user_id': user.id
        }, status=status.HTTP_200_OK)

        response_data = {
            'access': str(access),
            'refresh': str(refresh),
            'username': user.username,
            'user_id': user.id
        }

        request.session['user_info'] = {
            'username': user.username,
            'user_id': user.id,
            'is_superuser': user.is_superuser
        }

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            expires=timezone.now() + timedelta(days=1),
            secure=settings.SECURE_COOKIES,
            samesite='Lax',
        )

        if 'cart' in request.session:
            cart = request.session.pop('cart')
            request.session.flush() 
            request.session['cart'] = cart  

        login(request, user)
        if user.is_superuser or user.groups.filter(name='is_supervisor').exists():
            admin_url = request.build_absolute_uri(reverse('admin:index'))
            admin_redirect_url = f"{admin_url}?access_token={str(access)}"
            response_data['admin_url'] = admin_url

            return Response(response_data, status=status.HTTP_200_OK)

        return response


class UserCreateView(APIView):
    """API view to create a new user."""

    def post(self, request):
        """
        Create a new user.

        Args:
            request: The HTTP request object containing user data.

        Returns:
            Response: A Response object with the status of the creation.
        """
        phone_number = request.data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'message': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({'message': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response({'message': 'User with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        if User.objects.filter(password=password).exists():
            return Response({'message': 'User with this password already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)

        return Response({'message': 'There is a problem'}, status=status.HTTP_400_BAD_REQUEST)


class GenerateCodeView(APIView):
    """API view to generate and send a one-time code for email verification."""

    def post(self, request):
        """
        Generate a one-time code and send it to the user's email.

        Args:
            request: The HTTP request object containing the user's email.

        Returns:
            Response: A Response object with the status of the operation.
        """
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        
        code = ''.join(random.choices(string.digits, k=6))
        
        
        cache.set(email, code, timeout=300)

        
        send_mail(
            'Your One-Time Code',
            f'Your one-time code is: {code}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'Code sent to your email.'}, status=status.HTTP_200_OK)



class ValidateCodeView(APIView):
    """API view to validate the one-time code sent to the user's email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate the one-time code sent to the user's email and log in the user.

        Args:
            request: The HTTP request object containing email and code.

        Returns:
            Response: A Response object with access and refresh tokens if valid.
        """
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'message': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = cache.get(email)

        if stored_code == code and User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access.set_exp(lifetime=timedelta(hours=8))

            response = Response({
                'access': str(access),
                'refresh': str(refresh),
                'username': user.username,
                'user_id': user.id
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                expires=timezone.now() + timedelta(days=1),
                secure=settings.SECURE_COOKIES,
                samesite='Lax',
            )

            request.session['user_id'] = user.id
            cache.delete(email)
            return response

        elif stored_code == code and not User.objects.filter(email=email).exists():
            new_user = User(
                username=email.split('@')[0],
                email=email,
                password=email,
                role="c",
            )
            new_user.save()

            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access.set_exp(lifetime=timedelta(hours=8))

            response = Response({
                'access': str(access),
                'refresh': str(refresh),
                'username': user.username,
                'user_id': user.id
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                expires=timezone.now() + timedelta(days=1),
                secure=settings.SECURE_COOKIES,
                samesite='Lax',
            )

            request.session['user_id'] = user.id
            cache.delete(email)
            return response
        else:
            return Response({'message': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)


class TokenInfoView(APIView):
    """API view to retrieve information about a token."""

    permission_classes = [AllowAny]
    serializer_class = TokenInfoSerializer

    def post(self, request, *args, **kwargs):
        """
        Validate a token and return user information.

        Args:
            request: The HTTP request object containing the token.

        Returns:
            Response: A Response object containing user information if valid.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']

        try:
            validated_token = UntypedToken(token)
            user_id = validated_token['user_id']
            user = User.objects.get(id=user_id)

            expiration = validated_token.get('exp')
            expiration_datetime = timezone.make_aware(timezone.datetime.fromtimestamp(expiration))
            is_valid = timezone.now() < expiration_datetime

            return Response({
                'username': user.username,
                'expiration': is_valid,
                'user_id': user_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserInfo(APIView):
    """API view to retrieve a user's information."""
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        """
        Retrieve information for a specific user.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user whose information to retrieve.

        Returns:
            Response: A Response object containing user information.
        """
        data = User.objects.filter(id=user_id)
        serializer = UserSerializer(data, many=True)
        return Response(serializer.data)


class UpdateUserInfo(APIView):
    """API view to update a user's information."""
    permission_classes = [IsAuthenticated]
    def put(self, request, user_id):
        """
        Update information for a specific user.

        Args:
            request: The HTTP request object containing user data.
            user_id: The ID of the user to update.

        Returns:
            Response: A Response object with the status of the update.
        """
        user = get_object_or_404(User, id=user_id, is_delete=False)

        phone_number = request.data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=user_id).exists():
            return Response({'message': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            return Response({'message': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        if username and User.objects.filter(username=username).exclude(id=user_id).exists():
            return Response({'message': 'User with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'id': user.id, 'message': 'User updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'message': 'There is a problem'}, status=status.HTTP_400_BAD_REQUEST)


class UserUpdatePassView(APIView):
    """API view to update a user's password."""
    permission_classes = [IsAuthenticated]
    def put(self, request, user_id):
        """
        Update the password for a specific user.

        Args:
            request: The HTTP request object containing the new password.
            user_id: The ID of the user whose password is to be updated.

        Returns:
            Response: A Response object with the status of the update.
        """
        user = get_object_or_404(User, id=user_id)

        password = request.data.get('password')
        if User.objects.exclude(id=user_id).filter(password=password).exists():
            return Response({'message': 'User with this password already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserUpdatePassSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'id': user.id, 'message': 'User updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'message': 'There is a problem'}, status=status.HTTP_400_BAD_REQUEST)


class HeroGalleryView(APIView):
    """API view to retrieve active hero gallery items."""
    
    def get(self, request, format=None):
        """
        Retrieve all active hero gallery items.

        Args:
            request: The HTTP request object.
            format: The format of the response (optional).

        Returns:
            Response: A Response object containing hero gallery data.
        """
        data = HeroGallery.objects.filter(is_active=True)
        serializer = HeroGallerySerializer(data, many=True)
        return Response(serializer.data)