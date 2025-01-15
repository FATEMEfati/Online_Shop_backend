from django.contrib import admin
from .models import Orders, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Inline admin interface for OrderItem model.

    This class allows OrderItem instances to be edited inline within the Orders admin interface.
    It displays the OrderItem model in a tabular format and provides options to add extra items.
    """
    
    model = OrderItem
    extra = 1  
    exclude = ('deleted_at', 'price_at_order')

class OrdersAdmin(admin.ModelAdmin):
    """
    Admin interface for Orders model.

    This class customizes the admin interface for the Orders model, allowing
    for listing, searching, and filtering of order entries. It also includes
    an inline interface for editing related OrderItem instances.
    """
    
    list_display = ('id', 'user', 'pay_status', 'send_status', 'total_price')
    search_fields = ('user__username', 'id', 'receiver', 'address__city')
    list_filter = ('pay_status', 'send_status', 'city')
    inlines = [OrderItemInline]  
    exclude = ('deleted_at', 'city', 'street_name', "postal_code", "address_description")

    def save_model(self, request, obj, form, change):
        """
        Save the Orders model instance and calculate total price.

        This method overrides the default save behavior to ensure that the
        total price of the order is recalculated whenever an order is saved.

        Args:
            request: The HTTP request object.
            obj: The Orders model instance to be saved.
            form: The form containing the data to be saved.
            change: A boolean indicating whether this is a change to an existing instance.
        """
        super().save_model(request, obj, form, change)
        obj.calculate_total_price()  

class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for OrderItem model.

    This class customizes the admin interface for the OrderItem model, allowing
    for listing and searching of order items associated with orders.
    """
    
    list_display = ('order', 'item', 'quantity', 'price_at_order')
    search_fields = ('order__id', 'item__product_name')
    exclude = ('deleted_at',)


admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderItem, OrderItemAdmin)