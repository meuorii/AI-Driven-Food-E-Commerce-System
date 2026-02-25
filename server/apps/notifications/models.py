from django.db import models

# Create your models here.
class NotificationsNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('users.UsersUser', models.DO_NOTHING)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notifications_notification'