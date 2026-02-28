from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, ChangePasswordSerializer, AdminUserSerializer, ProfileUpdateSerializer, CustomerHistorySerializer, VendorHistorySerializer
from .models import UsersUser, UsersCustomerprofile, UsersVendorprofile
from .permissions import IsAdmin
from apps.vendors.models import VendorsStall
from apps.vendors.serializers import VendorStallSerializer

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
                "gender": profile.gender,
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
                "gender": profile.gender,
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
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        expires_at = timezone.now() + access_token.lifetime
        return Response({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "last_login": user.last_login
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "expires_at": expires_at.isoformat()
            },
            "message": "Login successful"
        }, status=status.HTTP_200_OK)
    
#Forget Password View
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data = request.data,
            context = {'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    
#User Profile ViewSet
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_profile(self, user):
        if user.role == 'CUSTOMER':
            return UsersCustomerprofile.objects.get(user=user)
        elif user.role == 'VENDOR':
            return UsersVendorprofile.objects.get(user=user)
        return None
    
    def get(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({"error": "Profile not found"}, status=404)
        
        serializer = ProfileUpdateSerializer(profile)
        return Response(serializer.data)
    
    def patch(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({"error": "Profile not found"}, status=404)
        
        if request.user.role == 'CUSTOMER':
            serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        else: 
            serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#Profile History View
class ProfileHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            if user.role == 'CUSTOMER':
                profile = user.customer_profile
                history_qs = profile.history.all().order_by('-history_date')
                serializer = CustomerHistorySerializer(history_qs, many=True)
            else: 
                profile = user.vendor_profile
                history_qs = profile.history.all().order_by('-history_date')
                serializer = VendorHistorySerializer(history_qs, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except (UsersCustomerprofile.DoesNotExist, UsersVendorprofile.DoesNotExist):
            return Response({"error": "Profile not found"}, status=404)

    
#Admin User Management ViewSet
class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = UsersUser.objects.exclude(role='ADMIN')\
            .select_related('customer_profile', 'vendor_profile')\
            .order_by('-created_at')
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
        user = get_object_or_404(UsersUser, pk=pk)

        if user.role == 'ADMIN':
            return Response({"detail": "Cannot delete an admin."}, status=status.HTTP_400_BAD_REQUEST)
        email = user.email
        if hasattr(user, 'customer_profile'):
            user.customer_profile.delete()
        if hasattr(user, 'vendor_profile'):
            user.vendor_profile.delete()

        user.delete()
        return Response({"detail": f"{email} deleted successfully."}, status=status.HTTP_200_OK)
    
    #Approve Vendor
    @action(detail=True, methods=['post'], url_path='approve-vendor')
    def approve_vendor(self, request, pk=None):
        user = self.get_object()
        if user.role != 'VENDOR':
            return Response({"detail": "User is not a vendor."}, status=status.HTTP_400_BAD_REQUEST)
        
        vendor_profile = getattr(user, 'vendor_profile', None)
        if not vendor_profile:
            return Response({"detail": "Vendor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        vendor_profile.is_approved = True
        vendor_profile.save(update_fields=['is_approved'])
        return Response({"detail": f"Vendor {user.email} approved successfully."}, status=status.HTTP_200_OK)
    
    #Reject Vendor
    @action(detail=True, methods=['post'], url_path='reject-vendor')
    def reject_vendor(self, request, pk=None):
        user = self.get_object()
        if user.role != 'VENDOR':
            return Response({"detail": "User is not a vendor."}, status=status.HTTP_400_BAD_REQUEST)
        
        vendor_profile = getattr(user, 'vendor_profile', None)
        if not vendor_profile:
            return Response({"detail": "Vendor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        vendor_profile.is_approved = False
        vendor_profile.save(update_fields=['is_approved'])
        return Response({"detail": f"Vendor {user.email} rejected successfully."}, status=status.HTTP_200_OK)
    
    #Get Vendor Activities
    @action(detail=True, methods=['get'], url_path='vendor-activity')
    def vendor_activity(self, request, pk=None):
        user = self.get_object()
        if user.role != 'VENDOR':
            return Response({"detail": "User is not a vendor."}, status=status.HTTP_400_BAD_REQUEST)

        vendor_profile = getattr(user, 'vendor_profile', None)
        if not vendor_profile:
            return Response({"detail": "Vendor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        stalls = VendorsStall.objects.filter(vendor=vendor_profile)
        stall_data = VendorStallSerializer(stalls, many=True).data

        activity_data = {
            "is_approved": vendor_profile.is_approved,
            "profile_created": vendor_profile.created_at,
            "last_login": user.last_login,
            "stalls": stall_data,  
        }

        return Response(activity_data, status=status.HTTP_200_OK)
