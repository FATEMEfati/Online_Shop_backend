from django.db import models
from Core.models import BaseModel, BaseManager

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from django.conf import settings

class CategoryManager(BaseManager):
    """Manager class for Category model."""
    
    def active_categories(self):
        """
        Retrieve all active categories.

        Returns:
            QuerySet: A queryset of active categories.
        """
        return self.filter(is_active=True)

class ProductManager(BaseManager):
    """Manager class for Product model."""
    
    def available_products(self):
        """
        Retrieve all available (active) products.

        Returns:
            QuerySet: A queryset of available products.
        """
        return self.filter(is_active=True)

class ProductAttributeManager(BaseManager):
    """Manager class for ProductAttribute model."""
    
    def attributes_for_product(self, product):
        """
        Retrieve attributes associated with a given product.

        Args:
            product (Product): The product for which to retrieve attributes.

        Returns:
            QuerySet: A queryset of attributes for the specified product.
        """
        return self.filter(product=product)

class DiversityManager(BaseManager):
    """Manager class for Diversity model."""
    
    def diversities_for_product(self, product):
        """
        Retrieve diversities associated with a given product that are in stock.

        Args:
            product (Product): The product for which to retrieve diversities.

        Returns:
            QuerySet: A queryset of diversities for the specified product with inventory greater than zero.
        """
        return self.filter(product=product, inventory__gt=0)

class GalleryManager(BaseManager):
    """Manager class for Gallery model."""
    
    def banners(self):
        """
        Retrieve all gallery items that are marked as banners.

        Returns:
            QuerySet: A queryset of gallery items that are banners.
        """
        return self.filter(banner=True)

class Category(BaseModel):
    """Model representing a category of products."""
    
    category_name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = CategoryManager()

    def __str__(self):
        """String representation of the Category."""
        return f'Category {self.id} - name: {self.category_name}'

    def clear_cache(self):
        """
        Clear the cache related to this category.
        """
        cache.delete('category_list')
        cache.delete(f'category_items_{self.id}')
        cache.delete(f'products_in_category_{self.id}')

@receiver(post_save, sender=Category)
def clear_category_cache_on_save(sender, instance, **kwargs):
    """
    Signal receiver to clear category cache on save event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()

@receiver(post_delete, sender=Category)
def clear_category_cache_on_delete(sender, instance, **kwargs):
    """
    Signal receiver to clear category cache on delete event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()

class Product(BaseModel):
    """Model representing a product in a category."""
    
    product_name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    is_discount = models.BooleanField(default=False)
    price_after_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = ProductManager()
    
    def calculate_discount(self):
        """
        Calculate and update the product's discount status and price after discount.

        This method retrieves applicable discounts and updates the product's
        `is_discount` and `price_after_discount` fields accordingly.
        """
        from Discount.models import Discount
        applicable_discount = Discount.objects.filter(is_active=True, product=self, is_delete=False).first()
        if applicable_discount:
            self.is_discount = True
            self.price_after_discount = Discount.objects.apply_discount(self.price, applicable_discount.discount_value, applicable_discount.discount_type)
            self.save()
        else:
            self.is_discount = False
            self.price_after_discount = None  
            self.save()

    def __str__(self):
        """String representation of the Product."""
        return f'Product {self.id} - name: {self.product_name}'

    def clear_cache(self):
        """
        Clear the cache related to this product.
        """
        cache.delete(f'products_in_category_{self.category_id}')
        cache.delete(f'product_{self.id}')
        cache.delete('category_list')

    def update_cache(self):
        """
        Update the cache for this product.
        """
        cache.set(f'product_{self.id}', self)

@receiver(post_save, sender=Product)
def clear_product_cache_on_save(sender, instance, **kwargs):
    """
    Signal receiver to clear product cache on save event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()
    instance.update_cache()

@receiver(post_delete, sender=Product)
def clear_product_cache_on_delete(sender, instance, **kwargs):
    """
    Signal receiver to clear product cache on delete event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()

@receiver(pre_save, sender=Product)
def check_discount_change(sender, instance, **kwargs):
    """
    Signal receiver to check if the discount status has changed before saving.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.
    """
    if instance.pk: 
        previous = Product.objects.get(pk=instance.pk)
        instance._is_discount_changed = (previous.is_discount != instance.is_discount)
    else:
        instance._is_discount_changed = False

@receiver(post_save, sender=Product)
def clear_product_cache_on_discount_save(sender, instance, created, **kwargs):
    """
    Signal receiver to clear product cache if the discount status has changed on save.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being saved.
        created: Boolean indicating if the instance was created.
        **kwargs: Additional keyword arguments.
    """
    if getattr(instance, '_is_discount_changed', False):
        products = Product.objects.filter(discount=instance.is_discount)
        for product in products:
            product.clear_cache()
            product.update_cache()

@receiver(post_delete, sender=Product)
def clear_product_cache_on_discount_delete(sender, instance, **kwargs):
    """
    Signal receiver to clear product cache if the discount status has changed on delete.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    products = Product.objects.filter(discount=instance.is_discount)
    for product in products:
        product.clear_cache()
        product.update_cache()

class ProductAttribute(BaseModel):
    """Model representing an attribute of a product."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    key = models.CharField(max_length=50, null=True, blank=True)
    value = models.CharField(max_length=20, null=True, blank=True)

    objects = ProductAttributeManager()

    def __str__(self):
        """String representation of the ProductAttribute."""
        return f'ProductAttribute {self.id} saved successfully'

    def clear_cache(self):
        """
        Clear the cache related to this product attribute.
        """
        cache.delete(f'product_attributes_{self.product_id}')

@receiver(post_save, sender=ProductAttribute)
def clear_product_attribute_cache_on_save(sender, instance, **kwargs):
    """
    Signal receiver to clear product attribute cache on save event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being saved.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()

@receiver(post_delete, sender=ProductAttribute)
def clear_product_attribute_cache_on_delete(sender, instance, **kwargs):
    """
    Signal receiver to clear product attribute cache on delete event.

    Args:
        sender: The model class that sent the signal.
        instance: The instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    instance.clear_cache()
    
class Diversity(BaseModel):
    """Model representing the diversity of a product based on color and size."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=20, null=True, blank=True)
    inventory = models.BigIntegerField(default=1)

    objects = DiversityManager()

    def __str__(self):
        """String representation of the Diversity."""
        return f'ProductAtribute {self.id} - color: {self.color} - size:{self.size}'
    

class Gallery(BaseModel):
    """Model representing a gallery of images for a product."""
    
    product = models.ForeignKey(Product, name="product", on_delete=models.CASCADE)
    banner = models.BooleanField(default=False)
    picture = models.ImageField(upload_to='photos/')

    objects = GalleryManager()

    def __str__(self):
        """String representation of the Gallery."""
        return f'Gallery {self.id} - product: {self.product.product_name}'
    
    def save(self, *args, **kwargs):
        """
        Save the gallery image, ensuring that only one banner can be set per product.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        if self.banner:
            Gallery.objects.filter(product=self.product, banner=True).exclude(id=self.id).update(banner=False)
        super().save(*args, **kwargs)
                

