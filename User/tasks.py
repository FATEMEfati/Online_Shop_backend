from celery import shared_task
from django.utils import timezone
from .models import User 
from Products.models import Product, Diversity
from Orders.models import Orders 
from django.db.models import Q
from django.contrib.sessions.models import Session
from datetime import timedelta

@shared_task()
def delete_unactivated_users():
    """
    Deletes users who have not activated their accounts within a specified threshold.

    Users that are not active (is_active=False), not marked for deletion 
    (is_delete=False), and were created more than three days ago are marked 
    for deletion (is_delete=True). Each unactivated user is saved after 
    updating their deletion status.
    """
    threshold_date = timezone.now() - timezone.timedelta(days=3)
    unactivated_users = User.objects.filter(Q(is_active=False), Q(is_delete=False), created_at__lt=threshold_date)
    unactivated_users.is_delete = True 
    for user in unactivated_users:
        user.is_delete = True  
        user.save()

@shared_task()
def clear_old_cart_items():
    """
    Removes expired cart items from user sessions.

    This task iterates through all active sessions, checking the 'cart' 
    data stored in each session. If an item in the cart was added more than 
    one hour ago, it is deleted from the cart. The inventory of the corresponding 
    product in the Diversity model is updated to reflect the removed quantity. 
    If the cart becomes empty, the session is deleted; otherwise, the session 
    is modified and saved.
    """
    now = timezone.now()
    sessions = Session.objects.all()

    for new_session in sessions:
        session_data = new_session.get_decoded()
        cart = session_data.get('cart', {})
        if not isinstance(cart, dict):
            cart = {}
        
        items_to_delete = []
        products_to_update = []

        for item_id, item in cart.items():
            products_to_update.append((item['id'], item['quantity'],item['color'],item['size']))  

        for product_id, quantity,color,size in products_to_update:
            try:
                product = Diversity.objects.get(product_id=product_id,color=color,size=size)
                product.inventory += quantity  
                product.save()
            except Diversity.DoesNotExist:
                continue

            new_session.delete()  
@shared_task()
def delete_unpaid_orders():
    """
    Deletes unpaid orders that are older than a specified threshold.

    This task checks for unpaid orders that have been created more than 
    15 minutes ago and have a payment status of either "progressing" 
    or "canceled". Such orders are marked for deletion (is_delete=True). 
    The inventory of the products associated with each order item is 
    updated to reflect the quantity of products in the deleted order.
    """
    current_time = timezone.now()
    time_threshold = current_time - timedelta(minutes=15)
    
    unpaid_orders = Orders.objects.filter(
        created_at__lt=time_threshold,  
        pay_status__in=["progressing", "canceled"],
        is_delete=False
    )

    for order in unpaid_orders:
        order.is_delete = True
        order.save()

        for order_item in order.order_items.all():
            product = order_item.item_diversity
            product.inventory += order_item.quantity  
            product.save()

        
