from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckoutSerializer, OrderSerializer

# Create your views here.
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            order = serializer.save()
            response_data = OrderSerializer(order).data

            return Response(
                {
                    "message": "Order placed successfully",
                    "order": response_data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
