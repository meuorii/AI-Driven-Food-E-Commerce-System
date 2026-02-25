from rest_framework import serializers
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile
from django.contrib.auth import authenticate

# Register Accoumt Serializer
from rest_framework import serializers
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile

class RegisterSerializer(serializers.ModelSerializer):
    # User fields
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)

    # Customer fields
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)

    # Vendor fields
    business_name = serializers.CharField(required=False, allow_blank=True)
    business_address = serializers.CharField(required=False, allow_blank=True)

    # Name fields (common)
    first_name = serializers.CharField(required=False, allow_blank=True)
    middle_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    suffix = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UsersUser
        fields = [
            'email', 'password', 'role',
            'phone', 'address', 'date_of_birth',
            'business_name', 'business_address',
            'first_name', 'middle_name', 'last_name', 'suffix'
        ]

    def create(self, validated_data):
        role = validated_data.get('role', 'CUSTOMER')
        if role not in ['CUSTOMER', 'VENDOR']:
            role = 'CUSTOMER'

        # Create user
        user = UsersUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )

        # Prepare profile fields based on role
        profile_data = {
            'first_name': validated_data.pop('first_name', None),
            'middle_name': validated_data.pop('middle_name', None),
            'last_name': validated_data.pop('last_name', None),
            'suffix': validated_data.pop('suffix', None),
        }

        if role == 'CUSTOMER':
            profile_data.update({
                'phone': validated_data.pop('phone', None),
                'address': validated_data.pop('address', None),
                'date_of_birth': validated_data.pop('date_of_birth', None),
            })
            UsersCustomerprofile.objects.create(user=user, **profile_data)
        elif role == 'VENDOR':
            profile_data.update({
                'business_name': validated_data.pop('business_name', None),
                'business_address': validated_data.pop('business_address', None),
            })
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

# Admin User Serializer
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersUser
        fields = ['id', 'email', 'role', 'is_active', 'is_suspended', 'created_at']
        read_only_fields = ['id', 'created_at']

    def suspend(self):
        if not self.instance:
            raise serializers.ValidationError("No user instance provided.")

        if self.instance.role == 'ADMIN':
            raise serializers.ValidationError("Cannot suspend another admin.")

        if self.instance.is_suspended:
            raise serializers.ValidationError("User is already suspended.")

        self.instance.is_suspended = True
        self.instance.save()
        return self.instance

    def unsuspend(self):
        if not self.instance:
            raise serializers.ValidationError("No user instance provided.")

        if self.instance.role == 'ADMIN':
            raise serializers.ValidationError("Cannot unsuspend an admin.")

        if not self.instance.is_suspended:
            raise serializers.ValidationError("User is not suspended.")

        self.instance.is_suspended = False
        self.instance.save()
        return self.instance

    def delete_user(self):
        if not self.instance:
            raise serializers.ValidationError("No user instance provided.")

        if self.instance.role == 'ADMIN':
            raise serializers.ValidationError("Cannot delete another admin.")

        self.instance.delete()
        return self.instance