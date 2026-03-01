from django.urls import path
from .views import VendorStallView, VendorStallToggleView, AdminStallManagementViewSet

admin_stall_list = AdminStallManagementViewSet.as_view({ "get": "get_all_stalls" })
admin_stall_detail = AdminStallManagementViewSet.as_view({ "get": "get_stall_by_id" })
admin_stall_approve = AdminStallManagementViewSet.as_view({ "patch": "approve_stall" })
admin_stall_reject = AdminStallManagementViewSet.as_view({ "patch": "reject_stall" })

urlpatterns = [
    path('vendor/stalls/', VendorStallView.as_view(), name='vendor-stalls'),  # GET all or POST create
    path('vendor/stalls/<int:stall_id>/', VendorStallView.as_view(), name='vendor-stall-detail'),  # GET/PATCH single stall
    path('vendor/stalls/<int:stall_id>/toggle/', VendorStallToggleView.as_view(), name='vendor-stall-toggle'),  # P toggle open/close

    #Admin Stall Management
    path('admin/stalls/', admin_stall_list, name='admin-stall-list'),
    path('admin/stalls/<int:pk>/', admin_stall_detail, name='admin-stall-detail'),
    path('admin/stalls/<int:pk>/approve/', admin_stall_approve, name='admin-stall-approve'),
    path('admin/stalls/<int:pk>/reject/', admin_stall_reject, name='admin-stall-reject'),
]