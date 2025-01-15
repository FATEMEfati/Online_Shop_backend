from django.test import TestCase
from User.models import User, Address
from Discount.models import Gift_cart
from Products.models import Product, Diversity,Category
from .models import Orders, OrderItem
from django.utils import timezone

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