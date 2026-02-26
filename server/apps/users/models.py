from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from simple_history.models import HistoricalRecords

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='CUSTOMER', **extra_fields):
        if not email:
            raise ValueError('Ang email ay mandatory para sa registration.') 
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)  # use role argument directly
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, role='ADMIN', **extra_fields)
    

class UsersUser(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    role = models.CharField(max_length=20, default='CUSTOMER') 
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        managed = True
        db_table = 'users_user'

# Create your models here.
class UsersCustomerprofile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(UsersUser, on_delete=models.CASCADE, related_name='customer_profile')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/customers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'users_customerprofile'


class UsersVendorprofile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(UsersUser, on_delete=models.CASCADE, related_name='vendor_profile')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    business_name = models.CharField(max_length=255)
    business_address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/vendors/', blank=True, null=True)
    is_approved = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'users_vendorprofile'
