from django.test import TestCase
from .models import User, Comments, Address, HeroGallery
from Products.models import Product ,Category 
from django.contrib.auth import get_user_model

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            role='c',
            gender='m',
            date_of_birth='1990-01-01',
            phone_number='09123456789'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword123'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser@example.com')


class CommentsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        my_category = Category.objects.create(
            category_name='Test cat'
            )
        self.product = Product.objects.create(product_name='Test Product', price=100.00,category=my_category,description='fgh')
        self.comment = Comments.objects.create(
            type_comment='q',
            user=self.user,
            product=self.product,
            subject='Test Subject',
            content='This is a test comment.'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.subject, 'Test Subject')
        self.assertEqual(self.comment.content, 'This is a test comment.')

    def test_comment_str(self):
        self.assertEqual(str(self.comment), f'comment {self.comment.id} with Test Subject subject saved successfully')


class AddressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        self.address = Address.objects.create(
            user=self.user,
            city='Test City',
            street_name='Test Street',
            postal_code='123456',
            description='Test Address'
        )

    def test_address_creation(self):
        self.assertEqual(self.address.city, 'Test City')
        self.assertEqual(self.address.street_name, 'Test Street')

    def test_address_str(self):
        self.assertEqual(str(self.address), f'address {self.address.id} saved successfully')


class HeroGalleryModelTest(TestCase):
    def setUp(self):
        self.hero_gallery = HeroGallery.objects.create(
            picture_1='path/to/picture1.jpg',
            picture_2='path/to/picture2.jpg',
            picture_3='path/to/picture3.jpg',
            is_active=True
        )

    def test_hero_gallery_creation(self):
        self.assertTrue(self.hero_gallery.is_active)

    def test_hero_gallery_str(self):
        self.assertEqual(str(self.hero_gallery), f'HiroGallery {self.hero_gallery.id} - is_active: True')

    def test_only_one_active_hero_gallery(self):
        second_gallery = HeroGallery.objects.create(
            picture_1='path/to/picture4.jpg',
            picture_2='path/to/picture5.jpg',
            picture_3='path/to/picture6.jpg',
            is_active=True
        )
        self.assertTrue(second_gallery.is_active)
        # self.assertFalse(self.hero_gallery.is_active)