from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager
from django.contrib.auth.models import Group, Permission
class BaseModel(models.Model):

    is_delete = models.BooleanField(default= False)
    deleted_at = models.DateTimeField(null=True , blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_delete and not self.deleted_at:
            self.deleted_at = timezone.now()
        elif not self.is_delete:
            self.deleted_at = None

        super().save(*args, **kwargs)

class BaseUserModel(AbstractBaseUser, PermissionsMixin):

    is_delete = models.BooleanField(default= False)
    deleted_at = models.DateTimeField(null=True , blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_delete and not self.deleted_at:
            self.deleted_at = timezone.now()
        elif not self.is_delete:
            self.deleted_at = None


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

class BaseManagermodel(BaseUserManager):

    is_delete = models.BooleanField(default= False)
    deleted_at = models.DateTimeField(null=True , blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_delete and not self.deleted_at:
            self.deleted_at = timezone.now()
        elif not self.is_delete:
            self.deleted_at = None

        super().save(*args, **kwargs)


class BaseManager(models.Manager):
    pass


