from django.urls import path
from .views import (ProductList,DisversityList,CategoryList,
                    GalleryList,CategoryItems,ProductCat,
                    Product_details,Product_diversity_details,SearchItems,ProductAttributeList
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api-v1/products/', ProductList.as_view(), name='product-list'),
    path('api-v1/product_diversity/', DisversityList.as_view(), name='product-diversity-list'),
    path('api-v1/categories/', CategoryList.as_view(), name='category-list'),
    path('api-v1/galery/', GalleryList.as_view(), name='gallery-list'),
    path('api-v1/categories/<int:cat_id>/', CategoryItems.as_view(), name='category-detail'),
    path('api-v1/product_for_cat/<int:cat_id>/',ProductCat.as_view(),name='product_for_cat'),
    path('api-v1/product_details/<int:product_id>/',Product_details.as_view(),name='product_details'),
    path('api-v1/product_attribute_details/<int:product_id>/',ProductAttributeList.as_view(),name='product_attribute'),
    path('api-v1/product_diversity_details/<int:product_id>/',Product_diversity_details.as_view(),name='product_diversity_details'),
    path('api-v1/search', SearchItems.as_view(), name='search_items'),

]

