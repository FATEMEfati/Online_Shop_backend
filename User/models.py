from django.db import models
from Core.models import BaseModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from Products.models import Product
from django.contrib.auth.models import Group, Permission
from .validator import iran_phone_regex, is_valid_password
from django.db.models import Q
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _


class CommentsManager(models.Manager):
    """
    Manager for Comments model to handle querying related to comments.
    """

    def get_comments_by_user(self, user):
        """
        Retrieve comments made by a specific user.

        :param user: The user whose comments are to be retrieved.
        :return: QuerySet of comments made by the user.
        """
        return self.filter(user=user)

    def get_comments_for_product(self, product):
        """
        Retrieve comments for a specific product.

        :param product: The product whose comments are to be retrieved.
        :return: QuerySet of comments related to the product.
        """
        return self.filter(product=product)

    def get_questions(self):
        """
        Retrieve comments that are questions.

        :return: QuerySet of question-type comments.
        """
        return self.filter(type_comment='q')

    def get_opinions(self):
        """
        Retrieve comments that are opinions.

        :return: QuerySet of opinion-type comments.
        """
        return self.filter(type_comment='o')


class HeroGalleryManager(models.Manager):
    """
    Manager for HeroGallery model to handle querying related to hero galleries.
    """

    def active(self):
        """
        Returns a queryset of active HeroGallery instances.

        :return: QuerySet of active HeroGallery instances.
        """
        return self.filter(is_active=True)

    def count_active(self):
        """
        Returns the count of active HeroGallery instances.

        :return: Integer count of active HeroGallery instances.
        """
        return self.active().count()


class AddressManager(models.Manager):
    """
    Manager for Address model to handle querying related to addresses.
    """

    def get_addresses_by_user(self, user):
        """
        Retrieve addresses associated with a specific user.

        :param user: The user whose addresses are to be retrieved.
        :return: QuerySet of addresses belonging to the user.
        """
        return self.filter(user=user)

    def get_addresses_in_city(self, city):
        """
        Retrieve addresses located in a specific city.

        :param city: The name of the city to filter addresses.
        :return: QuerySet of addresses in the specified city.
        """
        return self.filter(city=city)

    def get_address_by_postal_code(self, postal_code):
        """
        Retrieve addresses associated with a specific postal code.

        :param postal_code: The postal code to filter addresses.
        :return: QuerySet of addresses with the given postal code.
        """
        return self.filter(postal_code=postal_code)


class UserManager(BaseUserManager):
    """
    Custom manager for User model to handle user creation.
    """

    def create_user(self, username, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.

        :param username: The username for the user.
        :param password: The password for the user.
        :param extra_fields: Additional fields to set on the user.
        :return: The created user instance.
        """
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and return a superuser with the given username, email, and password.

        :param username: The username for the superuser.
        :param password: The password for the superuser.
        :param extra_fields: Additional fields to set on the superuser.
        :return: The created superuser instance.
        """
        user = self.create_user(username, password, **extra_fields)
        user.role = "m"
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model that extends AbstractBaseUser and PermissionsMixin.
    
    Attributes:
        username (str): Unique username for the user.
        password (str): Password for the user (hashed).
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        role (str): Role of the user (manager, customer, or supervisor).
        gender (str): Gender of the user.
        date_of_birth (date): Birth date of the user.
        phone_number (Decimal): User's phone number.
        email (str): User's email (unique).
        point (Decimal): Points associated with the user.
        is_active (bool): Indicates if the user is active.
        is_superuser (bool): Indicates if the user is a superuser.
        is_staff (bool): Indicates if the user can log into the admin site.
    """

    ROLE = (
        ("m", "manager"),
        ("c", "customer"),
        ("s", "supervisor"),
    )

    GENDER = (
        ("m", "male"),
        ("f", "female"),
        ("u", "uncertain"),
    )

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # Use a longer length for hashed passwords
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(choices=ROLE, max_length=1)
    gender = models.CharField(choices=GENDER, max_length=1, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.DecimalField(max_digits=19, decimal_places=0, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    point = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'role', 'gender', 'date_of_birth', 'phone_number']

    objects = UserManager()

    def save(self, *args, **kwargs):
        """
        Override save method to add the user to a supervisor group if the role is supervisor.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        is_new_user = self.pk is None
        super().save(*args, **kwargs)

        if is_new_user and self.role == 's':
            supervisor_group, created = Group.objects.get_or_create(name='is_supervisor')
            self.groups.add(supervisor_group)

    def __str__(self):
        """
        Return a string representation of the user.

        :return: Email address of the user.
        """
        return self.email


class Comments(BaseModel):
    """
    Model representing comments made by users on products.
    
    Attributes:
        type_comment (str): Type of the comment (question or opinion).
        user (ForeignKey): The user who made the comment.
        product (ForeignKey): The product the comment is related to.
        parent (ForeignKey): The parent comment for threaded comments.
        subject (str): Subject of the comment.
        content (str): Content of the comment.
    """

    TYPE_COMMENT = (
        ("q", "question"),
        ("o", "opinion")
    )

    type_comment = models.CharField(max_length=1, choices=TYPE_COMMENT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=20)
    content = models.CharField(max_length=200)

    objects = CommentsManager()

    def __str__(self):
        """
        Return a string representation of the comment.

        :return: Description of the comment including its ID and subject.
        """
        return f'comment {self.id} with {self.subject} subject saved successfully'


class Address(BaseModel):
    """
    Model representing a user's address.
    
    Attributes:
        user (ForeignKey): The user associated with the address.
        city (str): The city of the address.
        street_name (str): The street name of the address.
        postal_code (Decimal): The postal code of the address.
        description (str): Additional description for the address.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    street_name = models.CharField(max_length=50)
    postal_code = models.DecimalField(max_digits=17, decimal_places=0)
    description = models.CharField(max_length=100)

    objects = AddressManager()

    def __str__(self):
        """
        Return a string representation of the address.

        :return: Description of the address including its ID.
        """
        return f'address {self.id} saved successfully'


class HeroGallery(BaseModel):
    """
    Model representing a gallery of hero images.
    
    Attributes:
        is_active (bool): Indicates if the gallery is active.
        picture_1 (ImageField): First hero image.
        picture_2 (ImageField): Second hero image.
        picture_3 (ImageField): Third hero image.
    """

    is_active = models.BooleanField(default=True)
    picture_1 = models.ImageField(upload_to='hiro/')
    picture_2 = models.ImageField(upload_to='hiro/')
    picture_3 = models.ImageField(upload_to='hiro/')

    objects = HeroGalleryManager()

    def save(self, *args, **kwargs):
        """
        Override save method to ensure only one active HeroGallery instance exists.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        """
        if self.is_active:
            HeroGallery.objects.filter(~Q(id=self.id), is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return a string representation of the HeroGallery.

        :return: Description of the HeroGallery including its ID and active status.
        """
        return f'HiroGallery {self.id} - is_active: {self.is_active}'
