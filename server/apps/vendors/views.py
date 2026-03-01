from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import VendorsStall
from .serializers import VendorStallSerializer
from .utils import log_vendor_activity
from apps.users.serializers import VendorProfileSerializer

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
            stall =serializer.save()

            log_vendor_activity(vendor=request.user.vendor_profile, action_type="Created stall", stall=stall)
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
            log_vendor_activity(vendor=request.user.vendor_profile, action_type="Updated stall", stall=stall)
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
        log_vendor_activity(vendor=request.user.vendor_profile, action_type="Toggled stall", stall=stall)
        return Response({
            "message": "Stall status updated successfully",
            "stall_id": stall.id,
            "is_open": stall.is_open
        }, status=200)
    
class AdminStallManagementViewSet(viewsets.ModelViewSet):
    queryset = VendorsStall.objects.all()
    serializer_class = VendorStallSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    #Get All Stalls
    @action(detail=False, methods=['get'], url_path='all-stalls')
    def get_all_stalls(self, request):
        stalls = VendorsStall.objects.all()
        response_data = []

        for stall in stalls:
            stall_serialized = VendorStallSerializer(stall).data
            vendor_profile = getattr(stall, 'vendor', None)
            vendor_serialized = VendorProfileSerializer(vendor_profile).data if vendor_profile else None

            response_data.append({
                "stall": stall_serialized,
                "vendor": vendor_serialized
            })

        return Response(response_data, status=status.HTTP_200_OK)
    
    #Get Single Stall ID
    @action(detail=True, methods=['get'], url_path='stall-details')
    def get_stall_by_id(self, request, pk=None):
        stall = self.get_object()
        stall_serialized = VendorStallSerializer(stall).data
        vendor_profile = getattr(stall, 'vendor', None)
        vendor_serialized = VendorProfileSerializer(vendor_profile).data if vendor_profile else None

        return Response({
            "stall": stall_serialized,
            "vendor": vendor_serialized
        }, status=status.HTTP_200_OK)

    # Approve Stall
    @action(detail=True, methods=['patch'], url_path='approve')
    def approve_stall(self, request, pk=None):
        stall = self.get_object()
        if stall.is_approved:
            return Response({"detail": "Stall is already approved."}, status=status.HTTP_400_BAD_REQUEST)

        stall.is_approved = True
        stall.save(update_fields=['is_approved'])

        log_vendor_activity(
            vendor=stall.vendor,
            action_type="Approved stall",
            stall=stall
        )

        stall_serialized = VendorStallSerializer(stall).data
        vendor_serialized = VendorProfileSerializer(stall.vendor).data if stall.vendor else None

        return Response({
            "detail": f"Stall '{stall.name}' approved successfully.",
            "stall": stall_serialized,
            "vendor": vendor_serialized
        }, status=status.HTTP_200_OK)
    
    # Reject Stall
    @action(detail=True, methods=['patch'], url_path='reject')
    def reject_stall(self, request, pk=None):
        stall = self.get_object()
        if not stall.is_approved:
            return Response({"detail": "Stall is already not approved."}, status=status.HTTP_400_BAD_REQUEST)

        stall.is_approved = False
        stall.save(update_fields=['is_approved'])

        log_vendor_activity(
            vendor=stall.vendor,
            action_type="Rejected stall",
            stall=stall
        )

        stall_serialized = VendorStallSerializer(stall).data
        vendor_serialized = VendorProfileSerializer(stall.vendor).data if stall.vendor else None

        return Response({
            "detail": f"Stall '{stall.name}' rejected successfully.",
            "stall": stall_serialized,
            "vendor": vendor_serialized
        }, status=status.HTTP_200_OK)
