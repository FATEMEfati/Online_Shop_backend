from django.contrib import admin
from .models import Gift_cart, Discount

class GiftCartAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Gift_cart instances.

    This class customizes the display and functionality of the Gift_cart model 
    in the Django admin panel.

    Attributes:
        list_display (tuple): Fields to be displayed in the admin list view.
        search_fields (tuple): Fields to be searched in the admin search bar.
        list_filter (tuple): Fields to filter the results in the admin list view.
        ordering (tuple): Default ordering of the results in the admin list view.
        exclude (tuple): Fields to be excluded from the admin forms.

    Methods:
        None - Inherits methods from ModelAdmin.
    """
    list_display = ('id', 'user', 'code', 'discount_type', 'min_amount', 'max_amount', 'value', 'end_date', 'is_active')
    search_fields = ('code', 'user__username',)
    list_filter = ('discount_type', 'end_date')
    ordering = ('-end_date',)
    exclude = ('deleted_at',)

class DiscountAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Discount instances.

    This class customizes the display and functionality of the Discount model 
    in the Django admin panel.

    Attributes:
        list_display (tuple): Fields to be displayed in the admin list view.
        search_fields (tuple): Fields to be searched in the admin search bar.
        list_filter (tuple): Fields to filter the results in the admin list view.
        ordering (tuple): Default ordering of the results in the admin list view.
        exclude (tuple): Fields to be excluded from the admin forms.

    Methods:
        None - Inherits methods from ModelAdmin.
    """
    list_display = ('id', 'discount_type', 'product', 'discount_value', 'is_active')
    search_fields = ('discount_type',)
    list_filter = ('discount_type',)
    ordering = ('-discount_value',)
    exclude = ('deleted_at',)


admin.site.register(Gift_cart, GiftCartAdmin)
admin.site.register(Discount, DiscountAdmin)