from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import NotificationsNotification
from .serializers import NotificationSerializer, AdminNotificationSerializer
from apps.users.models import UsersUser
from apps.users.permissions import IsAdmin

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifications = NotificationsNotification.objects.filter(user=request.user)
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() == 'true':
                notifications = notifications.filter(is_read=True)
            elif is_read.lower() == 'false':
                notifications = notifications.filter(is_read=False)
        notification_type = request.query_params.get('type')
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        unread_count = NotificationsNotification.objects.filter(user=request.user, is_read=False).count()
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            "role": request.user.role,
            "unread_count": unread_count,
            "total": notifications.count(),
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)
    
class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        notification = NotificationsNotification.objects.filter(pk=pk, user=request.user).first()
        if not notification:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
        if notification.is_read:
            return Response({"message": "Notification is already marked as read."}, status=status.HTTP_200_OK)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)

class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request):
        updated = NotificationsNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"message": f"{updated} notification(s) marked as read."}, status=status.HTTP_200_OK)
    
class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk=None):
        if pk:
            notification = NotificationsNotification.objects.filter(pk=pk, user=request.user).first()
            if not notification: 
                return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
            notification.delete()
            return Response({"message": "Notification deleted."}, status=status.HTTP_200_OK)
        deleted_count, _ = NotificationsNotification.objects.filter(user=request.user).delete()
        return Response({"message": f"{deleted_count} notification(s) deleted."}, status=status.HTTP_200_OK)
    
class AdminNotificationListView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        notifications = NotificationsNotification.objects.all().select_related('user', 'order')
        user_id = request.query_params.get('user_id')
        if user_id:
            notifications = notifications.filter(user__id=user_id)
        role = request.query_params.get('role')
        if role:
            notifications = notifications.filter(user__role=role.upper())
        notification_type = request.query_params.get('type')
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() == 'true':
                notifications = notifications.filter(is_read=True)
            elif is_read.lower() == 'false':
                notifications = notifications.filter(is_read=False)
        serializer = AdminNotificationSerializer(notifications, many=True)
        return Response({"total": notifications.count(), "notifications": serializer.data}, status=status.HTTP_200_OK)
    
class AdvertisementNotificationView(APIView):
    permission_classes = [IsAuthenticated]
    ADVERTISEMENT_TYPES = [
        'stall_approved',
        'stall_toggled',
        'category_created',
        'food_item_created',
        'food_item_toggled',
    ]
    def get(self, request):
        notifications = NotificationsNotification.objects.filter(user=request.user, notification_type__in=self.ADVERTISEMENT_TYPES)
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() == 'true':
                notifications = notifications.filter(is_read=True)
            elif is_read.lower() == 'false':
                notifications = notifications.filter(is_read=False)
        notification_type = request.query_params.get('type')
        if notification_type:
            notifications = notifications.filter(notification_type=notification_type)
        unread_count = notifications.filter(is_read=False).count()
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"unread_count": unread_count, "total": notifications.count(), "advertisements": serializer.data}, status=status.HTTP_200_OK)