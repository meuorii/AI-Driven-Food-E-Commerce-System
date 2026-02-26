from django.urls import path
from .views import RegisterView, LoginView, AdminUserViewSet, UserProfileView, ProfileHistoryView

admin_user_list = AdminUserViewSet.as_view({ "get": "list" })
admin_user_detail = AdminUserViewSet.as_view({ "get": "retrieve" })
admin_user_suspend = AdminUserViewSet.as_view({ "patch": "suspend_user" })
admin_user_unsuspend = AdminUserViewSet.as_view({ "patch": "unsuspend_user" })
admin_user_delete = AdminUserViewSet.as_view({ "delete": "delete_user" })


urlpatterns = [
    #Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/history/', ProfileHistoryView.as_view(), name='profile-history'),

    #Admin User Management
    path('admin/users/', admin_user_list, name='admin-user-list'),
    path('admin/users/<int:pk>/', admin_user_detail, name='admin-user-detail'),
    path('admin/users/<int:pk>/suspend/', admin_user_suspend, name='admin-user-suspend'),
    path('admin/users/<int:pk>/unsuspend/', admin_user_unsuspend, name='admin-user-unsuspend'),
    path('admin/users/<int:pk>/delete/', admin_user_delete, name='admin-user-delete'),
]