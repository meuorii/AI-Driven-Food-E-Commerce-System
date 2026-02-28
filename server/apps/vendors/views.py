from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import VendorsStall
from .serializers import VendorStallSerializer

#Vendor Stall Management
class VendorStallView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_stall(self, stall_id=None):
        if stall_id:
            try:
                return VendorsStall.objects.get(id=stall_id, vendor=self.request.user.vendor_profile)
            except VendorsStall.DoesNotExist:
                return None
        else:
            return VendorsStall.objects.filter(vendor=self.request.user.vendor_profile)

    # GET /vendor/stalls/ or GET /vendor/stalls/<stall_id>/
    def get(self, request, stall_id=None):
        stalls = self.get_stall(stall_id)
        if stalls is None or (hasattr(stalls, 'count') and stalls.count() == 0):
            return Response({"detail": "Stall(s) not found"}, status=404)
        serializer = VendorStallSerializer(stalls, many=isinstance(stalls, list) or hasattr(stalls, 'count'))
        return Response(serializer.data)

    # POST /vendor/stalls/ -> create stall
    def post(self, request):
        if VendorsStall.objects.filter(vendor=request.user.vendor_profile).exists():
            return Response({"error": "You already have a stall"}, status=400)

        data = request.data.copy()
        data['vendor'] = request.user.vendor_profile.id
        serializer = VendorStallSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Stall created successfully", "stall": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    # PATCH /vendor/stalls/<stall_id>/ -> update stall
    def patch(self, request, stall_id=None):
        if not stall_id:
            return Response({"error": "Stall ID required for update"}, status=400)

        stall = self.get_stall(stall_id)
        if not stall:
            return Response({"error": "Stall not found"}, status=404)

        data = request.data.copy()
        files = {}
        if 'logo' in request.FILES:
            files['logo'] = request.FILES['logo']
        if 'banner' in request.FILES:
            files['banner'] = request.FILES['banner']

        serializer = VendorStallSerializer(stall, data={**data, **files}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Stall updated successfully", "stall": serializer.data})
        return Response(serializer.errors, status=400)
    
#Stall Open/Close Toggle 
class VendorStallToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, stall_id):
        try:
            stall = VendorsStall.objects.get(id=stall_id, vendor=request.user.vendor_profile)
        except VendorsStall.DoesNotExist:
            return Response({"error": "Stall not found"}, status=404)

        stall.is_open = not stall.is_open
        stall.save(update_fields=['is_open'])

        return Response({
            "message": "Stall status updated successfully",
            "stall_id": stall.id,
            "is_open": stall.is_open
        }, status=200)
