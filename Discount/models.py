from django.db import models
from Core.models import BaseModel, BaseManager
from User.models import User
from Products.models import Product
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class GiftCartManager(BaseManager):
    """Manager for GiftCart model to handle gift cart related queries."""
    
    def active_gift_carts(self):
        """Return all active gift carts that have not expired."""
        return self.filter(end_date__gte=timezone.now().date())

    def gift_cart_by_user(self, user):
        """Return all gift carts associated with a specific user.

        Args:
            user (User): The user for whom to retrieve gift carts.

        Returns:
            QuerySet: A queryset of gift carts belonging to the user.
        """
        return self.filter(user=user)

    
class DiscountManager(BaseManager):
    """Manager for Discount model to handle discount related queries."""
    
    def active_discounts(self):
        """Return all active discounts."""
        return self.filter(is_active=True)

    def inactive_discounts(self):
        """Return all inactive discounts."""
        return self.filter(is_active=False)

    def percentage_discounts(self):
        """Return all percentage-based discounts."""
        return self.filter(discount_type='p')

    def amount_discounts(self):
        """Return all amount-based discounts."""
        return self.filter(discount_type='a')

    def for_product(self, product):
        """Return all discounts applicable for a specific product.

        Args:
            product (Product): The product for which to retrieve discounts.

        Returns:
            QuerySet: A queryset of discounts applicable to the product.
        """
        return self.filter(product=product)

    def apply_discount(self, product_price, discount_value, discount_type):
        """Calculate the final price after applying the discount.

        Args:
            product_price (Decimal): The original price of the product.
            discount_value (Decimal): The discount value to be applied.
            discount_type (str): The type of discount ('p' for percentage, 'a' for amount).

        Returns:
            Decimal: The final price after applying the discount.
        """
        if discount_type == 'p':
            return float(product_price) - (float(product_price) * float(discount_value / 100))
        elif discount_type == 'a':
            return product_price - discount_value
        return product_price

class Gift_cart(BaseModel):
    """Model representing a gift cart containing discounts."""
    
    DISCOUNT_CHOICE = (
        ("p", "percentage"),
        ("a", "amount")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.DecimalField(max_digits=10, decimal_places=0, unique=True)
    discount_type = models.CharField(max_length=1, choices=DISCOUNT_CHOICE)
    min_amount = models.DecimalField(max_digits=10, decimal_places=0)
    max_amount = models.DecimalField(max_digits=10, decimal_places=0)
    value = models.DecimalField(max_digits=10, decimal_places=0)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    objects = GiftCartManager()

    def __str__(self):
        """Return a string representation of the GiftCart instance."""
        return f'gift cart {self.id} with {self.code} code saved successfully'
    

class Discount(BaseModel):
    """Model representing a discount applicable to a product."""
    
    DISCOUNT_CHOICE = (
        ("p", "percentage"),
        ("a", "amount")
    )

    discount_type = models.CharField(max_length=1, choices=DISCOUNT_CHOICE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)

    objects = DiscountManager()

    def __str__(self):
        """Return a string representation of the Discount instance."""
        return f'discount {self.id} for {self.product} saved successfully'


@receiver(post_save, sender=Discount)
def update_product_discount_on_save(sender, instance, created, **kwargs):
    """Update the product's discount when a Discount instance is saved.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Discount): The instance of the Discount that was saved.
        created (bool): A boolean indicating if a new record was created.
        kwargs: Additional keyword arguments.
    """
    try:
        instance.product.calculate_discount()
    except ObjectDoesNotExist:
        pass  

@receiver(post_delete, sender=Discount)
def update_product_discount_on_delete(sender, instance, **kwargs):
    """Update the product's discount when a Discount instance is deleted.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Discount): The instance of the Discount that was deleted.
        kwargs: Additional keyword arguments.
    """
    try:
        instance.product.calculate_discount()
    except ObjectDoesNotExist:
        pass

