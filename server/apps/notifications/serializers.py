from rest_framework import serializers
from .models import NotificationsNotification

class NotificationSerializer(serializers.ModelSerializer):
    order_code = serializers.SerializerMethodField()
    class Meta:
        model = NotificationsNotification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "order",
            "order_code",
            "is_read",
            "created_at",
        ]
    def get_order_code(self, obj):
        return obj.order.order_code if obj.order else None
    
class AdminNotificationSerializer(serializers.ModelSerializer):
    order_code = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    class Meta:
        model = NotificationsNotification
        fields = [
            "id",
            "user_email",
            "user_role",
            "title",
            "message",
            "notification_type",
            "order",
            "order_code",
            "is_read",
            "created_at",
        ]
    def get_order_code(self, obj):
        return obj.order.order_code if obj.order else None
    def get_user_email(self, obj):
        return obj.user.email
    def get_user_role(self, obj):
        return obj.user.role