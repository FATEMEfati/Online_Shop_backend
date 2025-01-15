from rest_framework import serializers
from .models import User, Comments, Address, HeroGallery
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer handles the serialization and deserialization of 
    User instances, allowing for easy conversion between User objects 
    and JSON representations.
    """
    class Meta:
        model = User
        fields = '__all__'  


class CommentsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comments model.

    This serializer provides the functionality to convert Comments 
    instances to and from JSON format.
    """
    class Meta:
        model = Comments
        fields = '__all__' 


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.

    This serializer manages the serialization and deserialization 
    of Address instances, including custom create and update methods.
    """
    class Meta:
        model = Address
        fields = '__all__' 

    def create(self, validated_data):
        """
        Create and return a new Address instance.

        Args:
            validated_data (dict): A dictionary of validated data to 
            create the Address instance.

        Returns:
            Address: The newly created Address instance.
        """
        address = Address(**validated_data)
        address.save()
        return address
    
    def update(self, instance, validated_data):
        """
        Update and return an existing Address instance.

        Args:
            instance (Address): The Address instance to update.
            validated_data (dict): A dictionary of validated data to 
            update the Address instance.

        Returns:
            Address: The updated Address instance.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save the updated instance
        return instance


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    This serializer validates the username and password during user 
    authentication and provides access to the authenticated user.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validate the username and password.

        Args:
            attrs (dict): A dictionary containing the username and 
            password.

        Returns:
            dict: The validated attributes including the authenticated 
            user.

        Raises:
            serializers.ValidationError: If the username or password 
            is invalid.
        """
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError("Invalid username or password")
            else:
                raise serializers.ValidationError("Invalid password")

        attrs['user'] = user
        return attrs


class TokenInfoSerializer(serializers.Serializer):
    """
    Serializer for token information.

    This serializer holds a single field for a token string, 
    typically used for authentication purposes.
    """
    token = serializers.CharField()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    This serializer handles the creation of new User instances, 
    including password hashing before saving the user to the database.
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 
                  'gender', 'date_of_birth', 'phone_number', 'email']

    def create(self, validated_data):
        """
        Create and return a new User instance with hashed password.

        Args:
            validated_data (dict): A dictionary of validated user data.

        Returns:
            User: The newly created User instance.
        """
        validated_data['password'] = make_password(validated_data['password'])
        user = User(**validated_data)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.

    This serializer allows for partial updates of User instances 
    without modifying the password.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 
                  'gender', 'date_of_birth', 'phone_number', 'email']


class UserUpdatePassSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a user's password.

    This serializer specifically handles the password update 
    functionality, ensuring the password is hashed before saving.
    """
    class Meta:
        model = User
        fields = ['password']

    def update(self, instance, validated_data):
        """
        Update and return the user's password.

        Args:
            instance (User): The User instance to update.
            validated_data (dict): A dictionary containing the new 
            password.

        Returns:
            User: The updated User instance.
        """
        instance.password = make_password(validated_data['password'])
        instance.save()
        return instance


class HeroGallerySerializer(serializers.ModelSerializer):
    """
    Serializer for the HeroGallery model.

    This serializer provides the functionality to convert HeroGallery 
    instances to and from JSON format.
    """
    class Meta:
        model = HeroGallery
        fields = '__all__'