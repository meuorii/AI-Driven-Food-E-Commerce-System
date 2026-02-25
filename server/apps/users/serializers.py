from rest_framework import serializers
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile
from django.contrib.auth import authenticate

# Register Accoumt Serializer
from rest_framework import serializers
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    business_name = serializers.CharField(required=False, allow_blank=True)
    business_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UsersUser
        fields = ['email', 'password', 'role', 'phone', 'address', 'date_of_birth', 'business_name', 'business_address']

    def create(self, validated_data):
        profile_data = {}
        if 'phone' in validated_data:
            profile_data['phone'] = validated_data.pop('phone')
        if 'address' in validated_data:
            profile_data['address'] = validated_data.pop('address')
        if 'date_of_birth' in validated_data:
            profile_data['date_of_birth'] = validated_data.pop('date_of_birth')
        if 'business_name' in validated_data:
            profile_data['business_name'] = validated_data.pop('business_name')
        if 'business_address' in validated_data:
            profile_data['business_address'] = validated_data.pop('business_address')

        # Role safety check
        role = validated_data.get('role', 'CUSTOMER')
        if role not in ['CUSTOMER', 'VENDOR']:
            role = 'CUSTOMER'

        # Create user
        user = UsersUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )

        # Create profile with optional fields
        if user.role == 'CUSTOMER':
            UsersCustomerprofile.objects.create(user=user, **profile_data)
        elif user.role == 'VENDOR':
            UsersVendorprofile.objects.create(user=user, **profile_data)

        return user
    
# Login Account Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
        else:
            raise serializers.ValidationError("Must include email and password")
        
        attrs['user'] = user
        return attrs