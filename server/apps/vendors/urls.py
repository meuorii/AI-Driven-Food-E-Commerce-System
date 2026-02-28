from django.urls import path
from .views import VendorStallView, VendorStallToggleView

urlpatterns = [
    path('vendor/stalls/', VendorStallView.as_view(), name='vendor-stalls'),  # GET all or POST create
    path('vendor/stalls/<int:stall_id>/', VendorStallView.as_view(), name='vendor-stall-detail'),  # GET/PATCH single stall
    path('vendor/stalls/<int:stall_id>/toggle/', VendorStallToggleView.as_view(), name='vendor-stall-toggle'),  # P toggle open/close
]