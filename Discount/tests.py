from django.test import TestCase
from django.utils import timezone
from User.models import User
from Products.models import Product,Category
from .models import Gift_cart, Discount
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Gift_cart
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime
class GiftCartModelTest(TestCase):
    def setUp(self):
        """Create a user for testing and a gift cart."""
        my_category = Category.objects.create(
            category_name='Test cat'
            )
        self.user = User.objects.create(username='testuser',password='12345@qw',role='c',email='qwe3@gmail.com')
        self.product = Product.objects.create(product_name='Test Product', price=100.00,category=my_category,description='fgh')  
        self.gift_cart = Gift_cart.objects.create(
            user=self.user,
            code=1234567890,
            discount_type='p',
            min_amount=50,
            max_amount=150,
            value=20,
            end_date=timezone.now().date() + timezone.timedelta(days=10),
            is_active=True
        )

    def test_gift_cart_creation(self):
        """Test that the gift cart is created correctly."""
        self.assertIsInstance(self.gift_cart, Gift_cart)
        self.assertEqual(str(self.gift_cart), f'gift cart {self.gift_cart.id} with {self.gift_cart.code} code saved successfully')

    def test_active_gift_carts(self):
        """Test that the active_gift_carts manager method works."""
        active_gift_carts = Gift_cart.objects.active_gift_carts()
        self.assertIn(self.gift_cart, active_gift_carts)

class DiscountModelTest(TestCase):
    def setUp(self):
        """Create a user and product for testing and a discount."""
        my_category = Category.objects.create(
            category_name='Test cat'
            )
        self.user = User.objects.create(username='testuser',password='12345@qw',role='c',email='qwe3@gmail.com')
        self.product = Product.objects.create(product_name='Test Product', price=100.00,category=my_category,description='fgh')  
        self.discount = Discount.objects.create(
            discount_type='p',
            product=self.product,
            discount_value=Decimal(10.00),
            is_active=True
        )

    def test_discount_creation(self):
        """Test that the discount is created correctly."""
        self.assertIsInstance(self.discount, Discount)
        self.assertEqual(str(self.discount), f'discount {self.discount.id} for {self.product} saved successfully')

    def test_active_discounts(self):
        """Test that the active_discounts manager method works."""
        active_discounts = Discount.objects.active_discounts()
        self.assertIn(self.discount, active_discounts)

    def test_apply_discount_percentage(self):
        """Test that the apply_discount method calculates percentage discount correctly."""
        final_price = Discount.objects.apply_discount(100.00, 10.00, 'p')
        self.assertEqual(final_price, 90.00)

    def test_apply_discount_amount(self):
        """Test that the apply_discount method calculates amount discount correctly."""
        final_price = Discount.objects.apply_discount(100.00, 10.00, 'a')
        self.assertEqual(final_price, 90.00)

    def test_apply_discount_invalid_type(self):
        """Test that the apply_discount method returns original price for invalid discount type."""
        final_price = Discount.objects.apply_discount(100.00, 10.00, 'x')
        self.assertEqual(final_price, 100.00)

    # def test_discount_signals(self):
    #     """Test that the product's discount is updated when a Discount instance is saved or deleted."""
    #     pass  


class GiftCartListTests(APITestCase):
    """
    Test case for the GiftCartList API view.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = User.objects.create_user(username='testuser', password='12345@qw', email='qwe3@gmail.com')
        
        
        login_url = reverse('login')  
        login_data = {
            'username': 'testuser',
            'password': '12345@qw',
        }
        login_response = self.client.post(login_url, login_data)
        self.access_token = login_response.data['access']
        
        
        
        self.gift_cart_1 = Gift_cart.objects.create(
            user=self.user,
            code=1230400,
            discount_type='p',
            min_amount=50,
            max_amount=150,
            value=100,
            end_date=timezone.now().date() + timezone.timedelta(days=10),
            is_active=True
        )
        self.gift_cart_2 = Gift_cart.objects.create(
            user=self.user,
            code=120304000,
            discount_type='p',
            min_amount=50,
            max_amount=150,
            value=50,
            end_date=timezone.now().date() + timezone.timedelta(days=10),
            is_active=True
        )

    def test_get_gift_cart_list(self):
        """
        Test retrieving the list of gift carts.
        """
        url = reverse('gift-cart-list')  
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        expected_data = [
        {
        'id': self.gift_cart_1.id,
        'is_delete': False,
        'deleted_at': None,
        'created_at': self.gift_cart_1.created_at.isoformat().replace('+00:00', 'Z'),  # Ensure the correct format
        'updated_at': self.gift_cart_1.updated_at.isoformat().replace('+00:00', 'Z'),  # Ensure the correct format
        'code': '1230400',
        'discount_type': 'p',
        'min_amount': '50',
        'max_amount': '150',
        'value': '100',
        'end_date': self.gift_cart_1.end_date.isoformat().replace('+00:00', 'Z'),
        'is_active': True,
        'user': self.gift_cart_1.user.id  
        },
        {
        'id': self.gift_cart_2.id,
        'is_delete': False,
        'deleted_at': None,
        'created_at': self.gift_cart_2.created_at.isoformat().replace('+00:00', 'Z') ,
        'updated_at': self.gift_cart_2.updated_at.isoformat().replace('+00:00', 'Z'),
        'code': '120304000',
        'discount_type': 'p',
        'min_amount': '50',
        'max_amount': '150',
        'value': '50',
        'end_date': self.gift_cart_2.end_date.isoformat().replace('+00:00', 'Z') ,
        'is_active': True,
        'user': self.gift_cart_2.user.id  
        },
    ]
        self.assertEqual(response.data, expected_data)

    def test_get_gift_cart_list_unauthenticated(self):
        """
        Test that an unauthenticated user cannot access the gift cart list.
        """
        self.client.logout()  # Log out the user
        url = reverse('gift-cart-list')
        response = self.client.get(url)

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)