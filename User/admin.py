
from django.contrib import admin
from .models import User, Comments, Address, HeroGallery
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for managing User instances.

    This class customizes the Django admin interface for the User model,
    including fieldsets for user details, permissions, and account management.
    """
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'role', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    exclude = ('deleted_at',)


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Comments instances.

    This class customizes the Django admin interface for the Comments model,
    allowing for easy viewing, searching, and filtering of user comments on products.
    """
    
    list_display = ('type_comment', 'user', 'product', 'subject', 'content')
    search_fields = ('subject', 'content', 'user__first_name', 'user__last_name', 'product__name')
    list_filter = ('type_comment',)
    exclude = ('deleted_at',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Address instances.

    This class customizes the Django admin interface for the Address model,
    facilitating the management of user addresses with search capabilities.
    """
    
    list_display = ('user', 'city', 'street_name', 'postal_code', 'description')
    search_fields = ('user__first_name', 'user__last_name', 'city', 'street_name')
    exclude = ('deleted_at',)


@admin.register(HeroGallery)
class HeroGalleryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing HeroGallery instances.

    This class customizes the Django admin interface for the HeroGallery model,
    enabling the management of gallery images along with their active status.
    """
    
    list_display = ('id', 'is_active', 'picture_1', 'picture_2', 'picture_3')
    list_filter = ('is_active',)
    search_fields = ('id',)
    ordering = ('-id',)
    fields = ('is_active', 'picture_1', 'picture_2', 'picture_3')
    readonly_fields = ('id',)
    exclude = ('deleted_at',)

    def save_model(self, request, obj, form, change):
        """
        Save the HeroGallery instance.

        Overrides the default save_model method to handle any necessary logic
        before saving the HeroGallery instance, such as managing the is_active
        status. Calls the superclass's save_model function to ensure proper
        saving behavior.
        """
        # Call the save method from the model to handle is_active logic
        obj.save()
        super().save_model(request, obj, form, change)