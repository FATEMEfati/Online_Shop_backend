from django.contrib import admin
from .models import Category, Product, ProductAttribute, Gallery, Diversity

class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product categories.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields to search in the admin interface.
        exclude (tuple): Fields to exclude from the admin form.
    """
    list_display = ('id', 'category_name', 'parent', 'is_active')
    search_fields = ('category_name',)
    exclude = ('deleted_at',)

class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing products.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        list_filter (tuple): Fields to filter products in the admin interface.
        search_fields (tuple): Fields to search in the admin interface.
        exclude (tuple): Fields to exclude from the admin form.
    """
    list_display = ('id', 'product_name', 'category', 'price', 'is_active')
    list_filter = ('category',)
    search_fields = ('product_name',)
    exclude = ('deleted_at',)

class ProductdiversityAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product diversity attributes (like color and size).

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields to search in the admin interface.
        exclude (tuple): Fields to exclude from the admin form.
    """
    list_display = ('id', 'product', 'color', 'size',)
    search_fields = ('product__product_name', 'color', 'size',)
    exclude = ('deleted_at',)

class ProductattributeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product attributes (key-value pairs).

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields to search in the admin interface.
        exclude (tuple): Fields to exclude from the admin form.
    """
    list_display = ('id', 'product', 'key', 'value',)
    search_fields = ('product__product_name', 'key', 'value',)
    exclude = ('deleted_at',)

class GalleryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing product galleries (images).

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields to search in the admin interface.
        exclude (tuple): Fields to exclude from the admin form.
    """
    list_display = ('id', 'product', 'banner', 'picture',)
    search_fields = ('product__product_name',)
    exclude = ('deleted_at',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Diversity, ProductdiversityAdmin)
admin.site.register(ProductAttribute, ProductattributeAdmin)
admin.site.register(Gallery, GalleryAdmin)
