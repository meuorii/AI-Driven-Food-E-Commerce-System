from django.urls import path
from .views import RegisterView, LoginView, ChangePasswordView, AdminUserViewSet, UserProfileView, ProfileHistoryView

admin_user_list = AdminUserViewSet.as_view({ "get": "list" })
admin_user_detail = AdminUserViewSet.as_view({ "get": "retrieve" })
admin_user_suspend = AdminUserViewSet.as_view({ "patch": "suspend_user" })
admin_user_unsuspend = AdminUserViewSet.as_view({ "patch": "unsuspend_user" })
admin_user_delete = AdminUserViewSet.as_view({ "delete": "delete_user" })
admin_vendor_approve = AdminUserViewSet.as_view({ "post": "approve_vendor" })
admin_vendor_reject = AdminUserViewSet.as_view({ "post": "reject_vendor" })
admin_vendor_get_activity = AdminUserViewSet.as_view({ "get": "vendor_activity" })
admin_user_profile_history = AdminUserViewSet.as_view({ "get": "profile_history" })


urlpatterns = [
    #Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/history/', ProfileHistoryView.as_view(), name='profile-history'),

    #Admin User Management
    path('admin/users/', admin_user_list, name='admin-user-list'),
    path('admin/users/<int:pk>/', admin_user_detail, name='admin-user-detail'),
    path('admin/users/<int:pk>/suspend/', admin_user_suspend, name='admin-user-suspend'),
    path('admin/users/<int:pk>/unsuspend/', admin_user_unsuspend, name='admin-user-unsuspend'),
    path('admin/users/<int:pk>/delete/', admin_user_delete, name='admin-user-delete'),

    # Admin Vendor Management
    path('admin/users/<int:pk>/approve-vendor/', admin_vendor_approve, name='admin-vendor-approve'),
    path('admin/users/<int:pk>/reject-vendor/', admin_vendor_reject, name='admin-vendor-reject'),
    path('admin/users/<int:pk>/vendor-activity/', admin_vendor_get_activity, name='admin-vendor-activity'),

    # Admin Get User Profile History
    path('admin/users/<int:pk>/profile-history/', admin_user_profile_history, name='admin-user-profile-history'),
]