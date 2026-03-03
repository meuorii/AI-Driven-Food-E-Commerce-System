from django.urls import path
from .views import VendorCategoryView, VendorFoodItemView, VendorFoodItemByCategoryView

urlpatterns = [
    path('vendor/stalls/<int:stall_id>/categories/', VendorCategoryView.as_view(), name='vendor-category-list-create'),
    path('vendor/stalls/<int:stall_id>/categories/<int:category_id>/', VendorCategoryView.as_view(), name='vendor-category-detail'),

    path('vendor/fooditems/', VendorFoodItemView.as_view(), name='vendor-fooditem-list-create'),
    path('vendor/fooditems/<int:fooditem_id>/', VendorFoodItemView.as_view(), name='vendor-food-details'),

    path('vendor/categories/<int:category_id>/fooditems/', VendorFoodItemByCategoryView.as_view(), name='vendor-fooditems-by-category')
]