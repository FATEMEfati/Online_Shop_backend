from django.test import TestCase
from User.models import User, Address
from Discount.models import Gift_cart
from Products.models import Product, Diversity,Category
from .models import Orders, OrderItem
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class OrdersModelTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create(username='testuser',password='12345@qw',role='c',email='qwe3@gmail.com')

        
        self.address = Address.objects.create(
            user=self.user,
            city='Test City',
            street_name='Test Street',
            postal_code='12345',
            description='Test Address'
        )

        my_category = Category.objects.create(
            category_name='Test cat'
            )
        self.product = Product.objects.create(product_name='Test Product', price=100.00,category=my_category,description='fgh')  
        self.diversity = Diversity.objects.create(color='Test color',size='test size', inventory=3,product=self.product)

        
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

    def test_order_creation(self):
        
        order = Orders.objects.create(
            user=self.user,
            pay_status='paid',
            receiver='Test Receiver',
            gift_cart=self.gift_cart,
            address=self.address,
            send_status='p',
            total_price=0  
        )

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.pay_status, 'paid')
        self.assertEqual(order.receiver, 'Test Receiver')
        self.assertEqual(order.gift_cart, self.gift_cart)

    def test_order_total_price_without_discount(self):
       
        order = Orders.objects.create(
            user=self.user,
            pay_status='paid',
            receiver='Test Receiver',
            address=self.address,
            send_status='p',
            total_price=0  
        )

        
        order_item = OrderItem.objects.create(
            order=order,
            item=self.product,
            item_diversity=self.diversity,
            quantity=2,
            price_at_order=0  
        )

        
        order.calculate_total_price()
        order.save()

        self.assertEqual(order.total_price, 200)  

    def test_order_total_price_with_discount(self):
       
        order = Orders.objects.create(
            user=self.user,
            pay_status='paid',
            receiver='Test Receiver',
            gift_cart=self.gift_cart,
            address=self.address,
            send_status='p',
            total_price=0  
        )

        
        order_item = OrderItem.objects.create(
            order=order,
            item=self.product,
            item_diversity=self.diversity,
            quantity=2,
            price_at_order=0  
        )

        
        order.calculate_total_price()
        order.save()

        
        self.assertEqual(order.total_price, 200)  

    def test_order_item_price_calculation(self):
        
        order = Orders.objects.create(
            user=self.user,
            pay_status='paid',
            receiver='Test Receiver',
            address=self.address,
            send_status='p',
            total_price=0  
        )

        
        self.product.is_discount = True
        self.product.price_after_discount = 80  
        self.product.save()

        
        order_item = OrderItem.objects.create(
            order=order,
            item=self.product,
            item_diversity=self.diversity,
            quantity=3,
            price_at_order=0  
        )

        
        self.assertEqual(order_item.price_at_order, 240)  

    def test_order_item_string_representation(self):
        # Create order
        order = Orders.objects.create(
            user=self.user,
            pay_status='paid',
            receiver='Test Receiver',
            address=self.address,
            send_status='p',
            total_price=0  # will be calculated
        )

        
        order_item = OrderItem.objects.create(
            order=order,
            item=self.product,
            item_diversity=self.diversity,
            quantity=2,
            price_at_order=0  
        )

        self.assertEqual(str(order_item), '2 x Test Product at 200.0')  

class OrdersAPITests(APITestCase):

    def setUp(self):
        my_category = Category.objects.create(category_name='Test cat')
        self.user = User.objects.create_user(username='testuser', password='12345@qw', email='qwe3@gmail.com')
        self.product = Product.objects.create(product_name='Test Product', price=100.00, category=my_category, description='fgh')
        self.diversity = Diversity.objects.create(color='Test color', size='40', inventory=3, product=self.product)
        
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': '12345@qw',
        }
        login_response = self.client.post(login_url, login_data)
        self.access_token = login_response.data['access']
        self.address = Address.objects.create(
            user=self.user,
            city='Test City2',
            street_name='Test Street2',
            postal_code='1234562',
            description='Test Address2'
        )

    def test_get_orders(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        Orders.objects.create(user=self.user, address=self.address, receiver='John Doe')

        url = reverse('orders-list', args=[self.user.id])
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_order(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        order = Orders.objects.create(user=self.user, address=self.address, receiver='John Doe')

        url = reverse('delete_order', args=[order.id])
        response = self.client.delete(url, **headers)

        self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order.refresh_from_db()

    def test_order_item_list(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        order = Orders.objects.create(user=self.user, address=self.address, receiver='John Doe')
        OrderItem.objects.create(order=order, item=self.product, item_diversity=self.diversity, quantity=2)

        url = reverse('orderitem-list', args=[order.id])
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_top_product(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        # Assume that we have an order item to test the top product retrieval
        order = Orders.objects.create(user=self.user, address=self.address, receiver='John Doe')
        OrderItem.objects.create(order=order, item=self.product, item_diversity=self.diversity, quantity=5)

        url = reverse('top_product')  # Assume this is the correct URL for top products
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_category(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }
        
        order = Orders.objects.create(user=self.user, address=self.address, receiver='John Doe')
        OrderItem.objects.create(order=order, item=self.product, item_diversity=self.diversity, quantity=5)

        url = reverse('top_category')  # Assume this is the correct URL for top categories
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_add_to_cart(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        url = reverse('add_to_cart')  # Assume this is the correct URL for adding to cart
        cart_data = {
            'product_id': self.product.id,
            'quantity': 1,
            'size': self.diversity.size,
            'color': self.diversity.color,
        }
        response = self.client.post(url, data=cart_data, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_from_cart(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        # First, add to the cart
        self.test_add_to_cart()

        url = reverse('remove_from_cart')  # Assume this is the correct URL for removing from cart
        remove_data = {
            'product_id': self.product.id,
            'quantity': 1,
            'size': self.diversity.size,
            'color': self.diversity.color,
        }
        response = self.client.post(url, data=remove_data, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_from_cart(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        # First, add to the cart
        self.test_add_to_cart()

        url = reverse('delete_from_cart')  # Assume this is the correct URL for deleting from cart
        delete_data = {
            'product_id': self.product.id,
            'size': self.diversity.size,
            'color': self.diversity.color,
        }
        response = self.client.post(url, data=delete_data, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_total_price(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        # Simulate adding to cart
        cart = {
            f"{self.product.id}_{self.diversity.size}_{self.diversity.color}": {
                'id': self.product.id,
                'quantity': 2,
                'size': self.diversity.size,
                'color': self.diversity.color,
            }
        }
        self.client.session['cart'] = cart

        url = reverse('total_price')  # Assume this is the correct URL for total price
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, float)

    def test_show_cart(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        # Simulate adding to cart
        cart = {
            f"{self.product.id}_{self.diversity.size}_{self.diversity.color}": {
                'id': self.product.id,
                'quantity': 2,
                'size': self.diversity.size,
                'color': self.diversity.color,
            }
        }
        self.client.session['cart'] = cart

        url = reverse('show_cart')  # Assume this is the correct URL for showing the cart
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_number_of_products(self):
        headers = {
            'HTTP_CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'
        }

        # Simulate adding to cart
        cart = {
            f"{self.product.id}_{self.diversity.size}_{self.diversity.color}": {
                'id': self.product.id,
                'quantity': 2,
                'size': self.diversity.size,
                'color': self.diversity.color,
            }
        }
        self.client.session['cart'] = cart

        url = reverse('number_of_product')  # Assume this is the correct URL for counting products
        response = self.client.get(url, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.user.delete()
        self.product.delete()
        self.diversity.delete()