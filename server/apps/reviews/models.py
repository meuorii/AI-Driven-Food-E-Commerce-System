from django.db import models
from apps.products.models import ProductsFooditem

# Create your models here.
class ReviewsReview(models.Model):
    id = models.UUIDField(primary_key=True)
    customer = models.ForeignKey('users.UsersCustomerprofile', models.DO_NOTHING)
    food_item = models.ForeignKey(ProductsFooditem, models.DO_NOTHING)
    rating = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reviews_review'
