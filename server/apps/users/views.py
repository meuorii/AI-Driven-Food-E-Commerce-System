from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, AdminUserSerializer
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile
from .serializers import RegisterSerializer
from .permissions import IsAdmin

class RegisterView(generics.CreateAPIView):
    queryset = UsersUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Prepare role-specific profile data
        profile_data = {}
        if user.role == 'CUSTOMER':
            profile = UsersCustomerprofile.objects.get(user=user)
            profile_data = {
                "first_name": profile.first_name,
                "middle_name": profile.middle_name,
                "last_name": profile.last_name,
                "suffix": profile.suffix,
                "phone": profile.phone,
                "address": profile.address,
                "date_of_birth": profile.date_of_birth,
            }
        elif user.role == 'VENDOR':
            profile = UsersVendorprofile.objects.get(user=user)
            profile_data = {
                "first_name": profile.first_name,
                "middle_name": profile.middle_name,
                "last_name": profile.last_name,
                "suffix": profile.suffix,
                "business_name": profile.business_name,
                "business_address": profile.business_address,
                "is_approved": profile.is_approved,
            }

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role,
                },
                "profile": profile_data,
                "message": "User registered successfully. Profile created."
            },
            status=status.HTTP_201_CREATED
        )
    
class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
    

class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = UsersUser.objects.exclude(role='ADMIN').order_by('-created_at')
        role = self.request.query_params.get('role')
        if role in ['CUSTOMER', 'VENDOR']:
            queryset = queryset.filter(role=role)
        return queryset

    @action(detail=True, methods=['patch'], url_path='suspend')
    def suspend_user(self, request, pk=None):
        user = self.get_object()
        if user.role == 'ADMIN':
            return Response({"detail": "Cannot suspend an admin."}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_suspended:
            return Response({"detail": "User is already suspended."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_suspended = True
        user.save(update_fields=['is_suspended'])
        return Response({"detail": f"{user.email} suspended successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='unsuspend')
    def unsuspend_user(self, request, pk=None):
        user = self.get_object()
        if user.role == 'ADMIN':
            return Response({"detail": "Cannot unsuspend an admin."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_suspended:
            return Response({"detail": "User is not suspended."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_suspended = False
        user.save(update_fields=['is_suspended'])
        return Response({"detail": f"{user.email} unsuspended successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_user(self, request, pk=None):
        user = self.get_object()
        if user.role == 'ADMIN':
            return Response({"detail": "Cannot delete an admin."}, status=status.HTTP_400_BAD_REQUEST)

        email = user.email
        user.delete()
        return Response({"detail": f"{email} deleted successfully."}, status=status.HTTP_200_OK)
