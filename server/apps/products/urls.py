from django.urls import path
from .views import VendorCategoryView, VendorFoodItemView, VendorFoodItemToggleView, AllFoodItemsView, FoodItemsByStallView, FoodItemsByCategoryView, FoodItemsByStallAndCategoryView, CustomerStallListView, CustomerFoodItemListView

urlpatterns = [
    # Product Food Categories
    path('vendor/stalls/<int:stall_id>/categories/', VendorCategoryView.as_view(), name='vendor-category-list-create'),
    path('vendor/stalls/<int:stall_id>/categories/<int:category_id>/', VendorCategoryView.as_view(), name='vendor-category-detail'),
    
    # Product Food Items
    path('vendor/stalls/<int:stall_id>/fooditems/', VendorFoodItemView.as_view(), name='vendor-fooditems-by-stall'),
    path('vendor/stalls/<int:stall_id>/categories/<int:category_id>/fooditems/', VendorFoodItemView.as_view(), name='vendor-fooditems-by-stall-category'),
    path('vendor/stalls/<int:stall_id>/fooditems/<int:fooditem_id>/', VendorFoodItemView.as_view(), name='vendor-fooditem-detail'),
    path('vendor/stalls/<int:stall_id>/fooditems/<int:fooditem_id>/toggle/', VendorFoodItemToggleView.as_view(), name='vendor-fooditem-toggle'),

    #Get All Products
    path('vendor/fooditems/', AllFoodItemsView.as_view(), name='all_food_items'),
    path('vendor/fooditems/stall/<int:stall_id>/', FoodItemsByStallView.as_view(), name='food_items_by_stall'),
    path('vendor/fooditems/category/<int:category_id>/', FoodItemsByCategoryView.as_view(), name='food_items_by_category'),
    path('vendor/fooditems/stall/<int:stall_id>/category/<int:category_id>/', FoodItemsByStallAndCategoryView.as_view(), name='food_items_by_stall_and_category'),

    #Customer Get All Products and Stalls
    path('customer/stalls/', CustomerStallListView.as_view(), name='stalls-list'),
    path('customer/food-items/', CustomerFoodItemListView.as_view(), name='fooditems-list'),
]