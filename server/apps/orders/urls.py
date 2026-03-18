from django.urls import path
from .views import CheckoutView, CustomerOrdersView, CustomerCancelOrderView, VendorOrderView, RiderOrderView, AvailableRidersView

urlpatterns = [
    # Customers
    path("customer/checkout/", CheckoutView.as_view(), name="checkout"),
    path("customer/orders/", CustomerOrdersView.as_view(), name="customer-orders"),
    path("customer/orders/<int:order_id>/", CustomerOrdersView.as_view(), name="customer-order-detail"),
    path("customer/orders/<int:order_id>/cancel/", CustomerCancelOrderView.as_view(), name="customer-cancel-order"),

    # Vendors
    path("vendor/orders/", VendorOrderView.as_view(), name="vendor-orders"),
    path("vendor/orders/<int:order_id>/", VendorOrderView.as_view(), name="vendor-order-detail"),
    path("vendor/orders/<int:order_id>/<str:action>/", VendorOrderView.as_view(), name="vendor-order-action"),
    path("vendor/riders/available/", AvailableRidersView.as_view()),

    #Riders
    path("rider/orders/", RiderOrderView.as_view(), name="rider-orders"),
    path("rider/orders/<int:order_id>/", RiderOrderView.as_view(), name="rider-order-detail"),
    path("rider/orders/<int:order_id>/<str:action>/", RiderOrderView.as_view(), name="rider-order-action"),
]