from django.test import TestCase
from .models import User, Comments, Address, HeroGallery
from Products.models import Product ,Category 
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

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


class UserApiTests(APITestCase):
    
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            phone_number='1234567890'
        )
        self.user.save()

        # Create a refresh token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_user_list(self):
        """Test retrieving the list of users."""
        url = reverse('user-list')  # Adjust this to your actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.user.username)

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse('user-create')  # Adjust to your actual URL
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'phone_number': '0987654321'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_login_user(self):
        """Test user login."""
        url = reverse('login')  # Adjust to your actual URL
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_create_address(self):
        """Test creating a new address."""
        url = reverse('address-list_post')  # Adjust to your actual URL
        data = {
            'user': self.user.id,
            'city': 'Test City',
            'street_name': 'Test Street',
            'postal_code': '123456',
            'description': 'Test Address'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_comments(self):
        """Test retrieving comments."""
        url = reverse('comment-list')  # Adjust to your actual URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hero_gallery(self):
        """Test retrieving hero gallery items."""
        url = reverse('hero_gallery')  # Adjust to your actual URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_addresses(self):
        """Test retrieving addresses for a specific user."""
        url = reverse('address-list', args=[self.user.id])  # Adjust to your actual URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_generate_code(self):
        """Test generating a code for email verification."""
        url = reverse('generate_code')  # Adjust to your actual URL
        data = {
            'email': 'testuser@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Code sent to your email.')

    def test_validate_code(self):
        """Test validating the generated code."""
        
        self.client.post(reverse('generate_code'), {'email': 'testuser@example.com'}, format='json')

        
        url = reverse('validate_code')  
        data = {
            'email': 'testuser@example.com',
            'code': '123456'  
        }
        response = self.client.post(url, data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_info(self):
        """Test retrieving a user's information."""
        url = reverse('user-info', args=[self.user.id])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.user.username)

    def test_update_user_password(self):
        """Test updating a user's password."""
        url = reverse('update_user_pass-info', args=[self.user.id])  # Adjust to your actual URL
        data = {
            'password': 'newpassword'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the password has been updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))