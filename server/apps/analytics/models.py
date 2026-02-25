from django.db import models

# Create your models here.
class AnalyticsAigenerationlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    execution_date = models.DateField()
    customers_generated = models.IntegerField(blank=True, null=True)
    orders_generated = models.IntegerField(blank=True, null=True)
    reviews_generated = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analytics_aigenerationlog'


class AnalyticsDailyanalytics(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_orders = models.IntegerField(blank=True, null=True)
    new_customers = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analytics_dailyanalytics'


class AnalyticsFoodperformance(models.Model):
    id = models.BigAutoField(primary_key=True)
    food_item = models.ForeignKey('products.ProductsFooditem', models.DO_NOTHING)
    total_sold = models.IntegerField(blank=True, null=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analytics_foodperformance'


class AnalyticsVendoranalytics(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey('users.UsersVendorprofile', models.DO_NOTHING)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_orders = models.IntegerField(blank=True, null=True)
    best_selling_item = models.ForeignKey('products.ProductsFooditem', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analytics_vendoranalytics'