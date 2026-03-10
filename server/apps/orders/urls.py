from django.urls import path
from .views import CheckoutView

urlpatterns = [
    path("customer/checkout/", CheckoutView.as_view(), name="checkout"),
]