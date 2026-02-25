from django.db import models

# Create your models here.
class RecommendationsVendorrecommendation(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('users.UsersVendorprofile', models.DO_NOTHING)
    recommendation_text = models.TextField()
    recommendation_type = models.TextField()  # This field type is a guess.
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recommendations_vendorrecommendation'
