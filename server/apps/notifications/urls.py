from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationMarkAllReadView,
    NotificationDeleteView,
    AdminNotificationListView,
    AdvertisementNotificationView,
)

urlpatterns = [
    # All roles
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('notifications/delete-all/', NotificationDeleteView.as_view(), name='notification-delete-all'),

    # Advertisements
    path('notifications/advertisements/', AdvertisementNotificationView.as_view(), name='notification-advertisements'),

    # Admin only
    path('notifications/admin/all/', AdminNotificationListView.as_view(), name='admin-notification-list'),
]