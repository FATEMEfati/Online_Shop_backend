from Core.models import BaseModel, BaseManager
from django.db import models
from User.models import User,Address
from Discount.models import Gift_cart
from Products.models import Product, Diversity
from django.utils import timezone


class OrdersManager(BaseManager):
    """Manager for Orders model to retrieve orders based on payment status."""

    def paid_orders(self):
        """Returns all orders with a payment status of 'paid'."""
        return self.filter(pay_status='paid')

    def in_progress_orders(self):
        """Returns all orders with a payment status of 'progressing'."""
        return self.filter(pay_status='progressing')

    def canceled_orders(self):
        """Returns all orders with a payment status of 'canceled'."""
        return self.filter(pay_status='canceled')


class OrderItemManager(BaseManager):
    """Manager for OrderItem model to retrieve items related to a specific order."""

    def items_in_order(self, order_id):
        """Returns all items associated with a given order ID."""
        return self.filter(order_id=order_id)

    def total_items_in_order(self, order_id):
        """Calculates the total quantity of items in a specific order by order ID."""
        return self.filter(order_id=order_id).aggregate(total=models.Sum('quantity'))['total'] or 0


class Orders(BaseModel):
    """
    Model representing an order placed by a user.

    Attributes:
        user (ForeignKey): The user who placed the order.
        pay_status (CharField): The payment status of the order.
        receiver (CharField): The name of the person receiving the order.
        gift_cart (ForeignKey): The gift cart associated with the order, if any.
        address (ForeignKey): The address to which the order will be delivered.
        city (CharField): The city of the delivery address.
        street_name (CharField): The street name of the delivery address.
        postal_code (DecimalField): The postal code of the delivery address.
        address_description (CharField): Additional description of the delivery address.
        send_status (CharField): The shipping status of the order.
        total_price (DecimalField): The total price of the order.
    """

    PAY_CHOICES = (
        ("paid", "paid"),
        ("progressing", "progressing"),
        ("canceled", "canceled")
    )
    SEND_CHOICES = (
        ("p", "Processing"),
        ("l", "Leaving the warehouse"),
        ("d", "Delivered")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pay_status = models.CharField(max_length=11, choices=PAY_CHOICES)
    receiver = models.CharField(max_length=50, null=True, blank=True)
    gift_cart = models.ForeignKey(Gift_cart, on_delete=models.CASCADE, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    city = models.CharField(max_length=50, null=True, blank=True)
    street_name = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.DecimalField(max_digits=17, decimal_places=0, null=True, blank=True)
    address_description = models.CharField(max_length=150, null=True, blank=True)
    send_status = models.CharField(max_length=1, choices=SEND_CHOICES)
    total_price = models.DecimalField(max_digits=9, decimal_places=0, null=True, blank=True)

    objects = OrdersManager()

    def __str__(self):
        """Returns a string representation of the order, including its ID and total price."""
        return f'Order {self.id} - Total: {self.total_price}'
    
    def calculate_total_price(self):
        """
        Calculates the total price of the order based on the subtotal of all order items,
        and applies a discount if a valid gift card is associated with the order.

        The total price is updated in the 'total_price' field of the order instance.
        """
        total = sum(item.price_at_order for item in self.order_items.all())
        
        if self.gift_cart and self.gift_cart.user == self.user:
            current_date = timezone.now().date()
            if (self.gift_cart.min_amount <= total <= self.gift_cart.max_amount and
                    self.gift_cart.end_date >= current_date):
                if self.gift_cart.discount_type == "p": 
                    discount = (self.gift_cart.value / 100) * total
                    total -= discount
                elif self.gift_cart.discount_type == "a":  
                    total -= self.gift_cart.value
        elif self.gift_cart and self.gift_cart.user != self.user:
            return "gift_cart not found"
        
        self.total_price = total

    def save(self, *args, **kwargs):
        """
        Overrides the save method to calculate the total price before saving.

        If an address is provided, it updates the city, postal code, street name,
        and address description fields based on the associated address instance.
        """
        if self.address:
            self.city = self.address.city
            self.postal_code = self.address.postal_code
            self.street_name = self.address.street_name
            self.address_description = self.address.description
            
        super().save(*args, **kwargs)  
        self.calculate_total_price() 


class OrderItem(BaseModel):
    """
    Model representing an item within an order.

    Attributes:
        order (ForeignKey): The order to which the item belongs.
        item (ForeignKey): The product that is being ordered.
        item_diversity (ForeignKey): The diversity variant of the product.
        quantity (PositiveIntegerField): The quantity of the product ordered.
        price_at_order (DecimalField): The price of the item at the time of the order.
    """

    order = models.ForeignKey(
        Orders, related_name="order_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_diversity = models.ForeignKey(Diversity, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    objects = OrderItemManager()

    def save(self, *args, **kwargs):
        """
        Overrides the save method to calculate the price of the order item based on
        whether the item is discounted, and updates the total price of the associated order.
        """
        if self.item.is_discount:
            self.price_at_order = (
                self.item.price_after_discount * self.quantity
            )
        else:
            self.price_at_order = (
                self.item.price * self.quantity
            )  # Assuming item has a price attribute
        super().save(*args, **kwargs)
        if self.order:
            self.order.calculate_total_price()
            self.order.save()

    def __str__(self):
        """Returns a string representation of the order item, including its quantity and price."""
        return f'{self.quantity} x {self.item.product_name} at {self.price_at_order}'
    