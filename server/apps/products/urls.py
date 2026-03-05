from django.urls import path
from .views import VendorCategoryView, VendorFoodItemView, VendorFoodItemToggleView

urlpatterns = [
    # Product Food Categories
    path('vendor/stalls/<int:stall_id>/categories/', VendorCategoryView.as_view(), name='vendor-category-list-create'),
    path('vendor/stalls/<int:stall_id>/categories/<int:category_id>/', VendorCategoryView.as_view(), name='vendor-category-detail'),
    
    # Product Food Items
    path('vendor/stalls/<int:stall_id>/fooditems/', VendorFoodItemView.as_view(), name='vendor-fooditems-by-stall'),
    path('vendor/stalls/<int:stall_id>/categories/<int:category_id>/fooditems/', VendorFoodItemView.as_view(), name='vendor-fooditems-by-stall-category'),
    path('vendor/stalls/<int:stall_id>/fooditems/<int:fooditem_id>/', VendorFoodItemView.as_view(), name='vendor-fooditem-detail'),

    path('vendor/stalls/<int:stall_id>/fooditems/<int:fooditem_id>/toggle/', VendorFoodItemToggleView.as_view(), name='vendor-fooditem-toggle')
]