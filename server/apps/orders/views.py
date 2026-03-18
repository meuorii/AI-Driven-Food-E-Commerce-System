from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import OrdersOrder
from .serializers import CheckoutSerializer, OrderSerializer, VendorOrderSerializer, AvailableRidersSerializer
from apps.users.models import UsersRiderProfile

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
    
class CustomerOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        customer = request.user.customer_profile

        if order_id:
            try:
                order = OrdersOrder.objects.prefetch_related("items", "items__food_item").get(id=order_id, customer=customer)
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            
        orders = OrdersOrder.objects.filter(
            customer=customer
        ).prefetch_related(
            "items", "items__food_item"
        ).order_by("-created_at")

        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data}, status=status.HTTP_200_OK)

class CustomerCancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        customer = request.user.customer_profile
        try:
            order = OrdersOrder.objects.get(id=order_id, customer=customer)
            if order.status != "pending":
                return Response({"error": "You can only cancel pending orders"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "cancelled"
            order.cancelled_by = "customer"
            order.save()
            return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)
        except OrdersOrder.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

class VendorOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_vendor_stall(self):
        vendor = self.request.user.vendor_profile
        return vendor.vendorsstall_set.first()

    def get_order(self, order_id):
        vendor_stall = self.get_vendor_stall()
        return OrdersOrder.objects.filter(
            id=order_id,
            stall=vendor_stall
        ).exclude(status="cancelled", cancelled_by="customer").prefetch_related("items", "items__food_item").first()

    def get(self, request, order_id=None, **kwargs):
        vendor_stall = self.get_vendor_stall()
        if order_id:
            order = self.get_order(order_id)
            if not order:
                return Response({"error": "Order not found"}, status=404)
            serializer = VendorOrderSerializer(order, context={"request": request})
            return Response(serializer.data, status=200)
        orders = OrdersOrder.objects.filter(
            stall=vendor_stall).exclude(status="cancelled", cancelled_by="customer").prefetch_related("items", "items__food_item").order_by("-created_at")
        serializer = VendorOrderSerializer(orders, many=True, context={"request": request})
        return Response({"orders": serializer.data}, status=200)

    def post(self, request, order_id, action, **kwargs):
        vendor_stall = self.get_vendor_stall()
        order = self.get_order(order_id)
        if not order:
            return Response({"error": "Order not found"}, status=404)
        if action == "confirm":
            if order.status != "pending":
                return Response({"error": "Only pending orders can be confirmed"}, status=status.H)
            for item in order.items.filter(food_item__stall=vendor_stall):
                food_item = item.food_item
                if food_item.stock_quantity < item.quantity:
                    return Response({"error": f"Not enough stock for {food_item.name}"}, status=status.HTTP_400_BAD_REQUEST)
                food_item.stock_quantity -= item.quantity
                food_item.save()
            order.status = "confirmed"

        elif action == "cancel":
            if order.status not in ["pending", "confirmed"]:
                return Response({"error": "Cannot cancel order at this stage"}, status=400)
            if order.status == "confirmed":
                for item in order.items.filter(food_item__stall=vendor_stall):
                    food_item = item.food_item
                    food_item.stock_quantity += item.quantity
                    food_item.save()
            reason = request.data.get("reason")
            if not reason:
                return Response({"error": "Cancel reason is required"}, status=400)
            order.status = "cancelled"
            order.cancelled_by = "vendor"
            order.cancel_reason = reason
            order.save()
            return Response({"message": f"Order cancelled successfully with reason: {reason}"}, status=status.HTTP_200_OK)
        
        elif action == "prepare":
            if order.status != "confirmed":
                return Response({"error": "Order must be confirmed before preparing"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "preparing"

        elif action == "ready":
            if order.status != "preparing":
                return Response({"error": "Order must be preparing before marking ready"}, status=status.HTTP_400_BAD_REQUEST)
            if order.order_type == "delivery":
                rider_id = request.data.get("rider_id")
                if not rider_id:
                    return Response({"error": "rider_id is required for delivery orders"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    rider = UsersRiderProfile.objects.get(id=rider_id, is_available=True, is_approved=True)
                    order.rider = rider
                except UsersRiderProfile.DoesNotExist:
                    return Response({"error": "Rider not found or not available"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "ready_for_pickup"

        elif action == "complete":
            if order.order_type != "pickup":
                return Response({"error": "Only pickup orders can be completed by vendor"}, status=status.HTTP_400_BAD_REQUEST)
            if order.status != "ready_for_pickup":
                return Response({"error": "Order must be ready for pickup"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "completed"
            
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        order.save()
        return Response({"message": f"Order status updated to {order.status}"}, status=status.HTTP_200_OK)

class AvailableRidersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        riders = UsersRiderProfile.objects.filter(
            is_available=True,
            is_approved=True
        ).select_related("user")

        serializer = AvailableRidersSerializer(riders, many=True)
        return Response({"available_riders": serializer.data}, status=status.HTTP_200_OK)

class RiderOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_orders(self):
        return OrdersOrder.objects.filter(order_type="delivery").exclude(status="cancelled").prefetch_related("items", "items__food_item")
    
    def get(self, request, order_id=None, **kwargs):
        rider = getattr(request.user, "rider_profile", None)
        if not rider:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        if order_id:
            order = self.get_orders().filter(id=order_id).first()
            if not order:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        
        orders = self.get_orders().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response({"orders": serializer.data})
    
    def post(self, request, order_id, action, **kwargs):
        rider = getattr(request.user, "rider_profile", None)
        if not rider:
            return Response({"error": "Rider profile not found"}, status=status.HTTP_404_NOT_FOUND)
        order = OrdersOrder.objects.filter(id=order_id, order_type="delivery").first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if action == "picked_up":
            if order.status != "ready_for_pickup":
                return Response({"error": "Order must be picked up first"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "picked_up"
        
        elif action == "out_for_delivery":
            if order.status != "picked_up":
                return Response({"error": "Order must be picked up first"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "out_for_delivery"

        elif action == "complete":
            if order.status != "out_for_delivery":
                return Response({"error": "Order must be out for delivery"}, status=status.HTTP_400_BAD_REQUEST)
            order.status = "completed"

        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        
        order.save()
        return Response({"message": f"Order status updated to {order.status}"})
    
