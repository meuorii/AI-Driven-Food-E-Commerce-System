from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from .models import UsersUser
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from .models import UsersUser

class RegisterView(generics.CreateAPIView):
    queryset = UsersUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role
                },
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
