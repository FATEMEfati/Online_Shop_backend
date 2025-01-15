from django.test import TestCase
from .models import Category, Product, ProductAttribute, Diversity, Gallery
from django.core.cache import cache

class ModelsTestCase(TestCase):
    """Test case for the models in the application."""

    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(category_name="Electronics")
        self.product = Product.objects.create(
            product_name="Smartphone",
            category=self.category,
            price=699.99,
            description="Latest model smartphone"
        )
        self.product_attribute = ProductAttribute.objects.create(
            product=self.product,
            key="Color",
            value="Black"
        )
        self.diversity = Diversity.objects.create(
            product=self.product,
            color="Black",
            size="M",
            inventory=10
        )
        self.gallery = Gallery.objects.create(
            product=self.product,
            banner=True,
            picture="path/to/image.jpg"  
        )

    def test_category_creation(self):
        """Test creating a category."""
        self.assertEqual(self.category.category_name, "Electronics")
        self.assertTrue(self.category.is_active)

    def test_product_creation(self):
        """Test creating a product."""
        self.assertEqual(self.product.product_name, "Smartphone")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.price, 699.99)

    def test_product_attribute_creation(self):
        """Test creating a product attribute."""
        self.assertEqual(self.product_attribute.key, "Color")
        self.assertEqual(self.product_attribute.value, "Black")

    def test_diversity_creation(self):
        """Test creating a product diversity."""
        self.assertEqual(self.diversity.color, "Black")
        self.assertEqual(self.diversity.size, "M")
        self.assertEqual(self.diversity.inventory, 10)

    def test_gallery_creation(self):
        """Test creating a gallery."""
        self.assertTrue(self.gallery.banner)
        self.assertEqual(self.gallery.product, self.product)

    def test_cache_clear_on_category_save(self):
        """Test cache clear on category save."""
        cache.set('category_list', ['some data'])
        self.assertIn('category_list', cache)

        self.category.category_name = "Updated Electronics"
        self.category.save()
        
        self.assertNotIn('category_list', cache)

    # def test_cache_clear_on_product_save(self):
    #     """Test cache clear on product save."""
    #     cache.set(f'product_{self.product.id}', self.product)
    #     self.assertIn(f'product_{self.product.id}', cache)

    #     self.product.product_name = "Updated Smartphone"
    #     self.product.save()
        
    #     self.assertNotIn(f'product_{self.product.id}', cache)

    def test_discount_calculation(self):
        """Test discount calculation."""
        
        from Discount.models import Discount
        self.discount = Discount.objects.create(
            discount_type='p',
            product=self.product,
            discount_value=10.00,
            is_active=True
        )
        
        self.product.calculate_discount()
        self.assertTrue(self.product.is_discount)
        print(self.product.price_after_discount)
        self.assertEqual(self.product.price_after_discount, 629.991)  

    def tearDown(self):
        """Clean up after tests."""
        Category.objects.all().delete()
        Product.objects.all().delete()
        ProductAttribute.objects.all().delete()
        Diversity.objects.all().delete()
        Gallery.objects.all().delete()