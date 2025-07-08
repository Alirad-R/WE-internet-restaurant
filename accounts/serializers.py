# accounts/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import OTP, User, CustomerProfile

class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerProfile model
    """
    class Meta:
        model = CustomerProfile
        fields = ('id', 'phone_number', 'address', 'city', 'state', 'country', 
                 'postal_code', 'preferences', 'allergies', 'dietary_restrictions',
                 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer profile
    """
    class Meta:
        model = CustomerProfile
        fields = ('phone_number', 'address', 'city', 'state', 'country', 
                 'postal_code', 'preferences', 'allergies', 'dietary_restrictions')
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class UserWithProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with nested CustomerProfile
    """
    customer_profile = CustomerProfileSerializer()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'image', 
                 'date_of_birth', 'location', 'customer_profile')

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - used for GET operations
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'image', 'date_of_birth', 'location')

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name', 'image', 'date_of_birth', 'location')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            image=validated_data.get('image', None),
            date_of_birth=validated_data.get('date_of_birth', None),
            location=validated_data.get('location', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a user
    """
    email = serializers.EmailField(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'image', 'date_of_birth', 'location')
        extra_kwargs = {
            'username': {'required': False},
        }
    
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
        
    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value
        
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.image = validated_data.get('image', instance.image)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.location = validated_data.get('location', instance.location)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        
        if username is None:
            raise serializers.ValidationError('A username is required to log in.')
        
        if password is None:
            raise serializers.ValidationError('A password is required to log in.')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            raise serializers.ValidationError('A user with this username and password was not found.')
        
        if not user.is_active:
            raise serializers.ValidationError('This user has been deactivated.')
        
        return {
            'username': user.username,
            'user': user
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users with essential information for admin management
    """
    customer_profile = CustomerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'date_joined', 'last_login', 'customer_profile')
        read_only_fields = ('id', 'date_joined', 'last_login')