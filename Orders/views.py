from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Orders ,OrderItem
from Discount.models import Gift_cart
from Products.models import Category,Product,Diversity
from .serializers import OrderItemSerializer, OrdersSerializer,TopProductSerializer,CartSerializer,CreateOrdersSerializer
from Products.serializers import CategorySerializer
from datetime import timedelta
from django.db.models import Sum,F
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from decimal import Decimal
from rest_framework.authentication import TokenAuthentication
class OrdersList(APIView):
    """
    Retrieve a list of orders for a specific user.

    Methods
    -------
    get(request, user_id):
        Retrieves all orders for a given user that are not marked as deleted.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        data = Orders.objects.filter(user=user_id,is_delete=False)
        serializer = OrdersSerializer(data, many=True)
        return Response(serializer.data)
    
class DeleteOrder(APIView):
    """
    Delete an order by marking it as deleted and restoring the inventory of its items.

    Methods
    -------
    get(request, order_id):
        Marks the specified order as deleted and restores inventory for its items.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, order_id):
        try:
            order = Orders.objects.get(id=order_id, is_delete=False)
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                product = Diversity.objects.get(id=item.item_diversity_id)  
                product.inventory += item.quantity  
                product.save()
            
            order.is_delete = True
            order.save()

            return Response({"message": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Orders.DoesNotExist:
            return Response({"message": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        

    
class OrderItemList(APIView):
    """
    Retrieve a list of order items for a specific order.

    Methods
    -------
    get(request, order_id):
        Retrieves all order items for a given order that are not marked as deleted.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request,order_id):
        data = OrderItem.objects.filter(order=order_id,is_delete=False)
        serializer = OrderItemSerializer(data, many=True)
        return Response(serializer.data)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta
from .models import OrderItem  # Make sure to import your OrderItem model
from .serializers import TopProductSerializer  # Make sure to import your serializer

class TopProduct(APIView):
    """
    Retrieve the top-selling products in the last month.

    Methods
    -------
    get(request, format=None):
        Returns the top N products based on the quantity sold in the last 30 days,
        where N is specified by the query parameter or defaults to 10.
    """
    def get(self, request, format=None):
        now = timezone.now()
        last_month_start = now - timedelta(days=30)

        
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
            if limit < 9 or limit > 25:
                return Response({"error": "Limit must be between 10 and 25."}, status=400)
        except ValueError:
            return Response({"error": "Invalid limit value."}, status=400)

        products = (
            OrderItem.objects.filter(order__send_status='d', created_at__gte=last_month_start)
            .values('item__product_name', 'item__price', 'item__is_discount', 'item__price_after_discount', "quantity", "order", "item__id")
            .annotate(total_orders=Sum("quantity"))
            .annotate(total_price=Sum("quantity") * F("item__price"))
            .order_by("-total_orders")[:limit]  
        )
        
        serializer = TopProductSerializer(products, many=True)
        return Response(serializer.data)
    
class TopCategory(APIView):
    """
    Retrieve the top-selling product categories in the last month.

    Methods
    -------
    get(request, format=None):
        Returns the top 6 categories based on the quantity sold in the last 30 days.
    """
    def get(self, request, format=None):
        now = timezone.now()
        last_month_start = now - timedelta(days=30)
        top_categories = (
        OrderItem.objects
        .filter(order__send_status='d',created_at__gte=last_month_start)
        .values('item__category')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')
        )[:6]
        top_categories_with_details = []
        for category in top_categories:
            category_id = category['item__category']
            total_quantity = category['total_quantity']
            category_name = Category.objects.get(id=category_id).category_name
            top_categories_with_details.append({
                'id': category_id,
                'category_name': category_name,
                'total_quantity': total_quantity,
            })
        serializer = CategorySerializer(top_categories_with_details, many=True)
        return Response(serializer.data)
    


class OrderCreateView(APIView):
    """
    Create a new order based on the items in the cart.

    Methods
    -------
    post(request, *args, **kwargs):
        Creates a new order, processes the gift card if provided, and clears the cart.
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # Retrieve the cart from the session
        cart = request.session.get('cart', {})
        request.session['cart'] = cart
        

        if not cart:
            return Response({"message": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        gift_cart_code = request.data.get('gift_cart', None)
        shipping_address = request.data.get('address')
        receiver = request.data.get('receiver', None)
        user_id = request.data.get('user')

        gift_card_id = None  

        if gift_cart_code:
            try:
                gift_card = Gift_cart.objects.get(code=gift_cart_code)
                if gift_card.is_active:
                    gift_card_id = gift_card.id
                    gift_card.is_active = False
                    gift_card.save()
            except Gift_cart.DoesNotExist:
                return Response({"message": "Gift card not found."}, status=status.HTTP_404_NOT_FOUND)
        order_data = {
            'user': user_id,
            'address': shipping_address,
            'receiver': receiver,
            'gift_cart': gift_card_id,  
            'pay_status': 'progressing',  
            'send_status': 'p',
            "total_price": 0.00  
        }

        serializer = CreateOrdersSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()
            for item_data in cart.values():
                print("cart")
                product_id = item_data['id']
                quantity = item_data['quantity']
                size = item_data['size']
                color = item_data['color']
                
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response({"message": f"Product with ID {product_id} not found."}, status=status.HTTP_404_NOT_FOUND)

                try:
                    product_diversity = Diversity.objects.get(product_id=product_id,size=size,color=color)
                except Diversity.DoesNotExist:
                    return Response({"message": f"Product with ID {product_id} not found."}, status=status.HTTP_404_NOT_FOUND)
                

                order_item = OrderItem(order=order, item=product,item_diversity=product_diversity, quantity=quantity)
                order_item.save()  

            
            order.save()
            cart.clear()
            return Response({
                'id': order.id,
                'total_price': str(order.total_price),
                'message': 'Order created successfully!'
            }, status=status.HTTP_201_CREATED)

        return Response({"message": "There is a problem"},status=status.HTTP_400_BAD_REQUEST)



class AddToCart(APIView):
    """
    Add a product to the user's cart in the session.

    Methods
    -------
    post(request):
        Adds a specified product to the cart, updating inventory and session data.
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        size = request.data.get('size')
        color = request.data.get('color')

        try:
            product = Diversity.objects.get(product_id=product_id,color = color, size=size)
        except Diversity.DoesNotExist:
            return Response({"message": "Please make sure you choose the right color and size"}, status=404)

        if product.inventory < quantity:
            return Response({"message": "Not enough inventory."}, status=400)
        
        try:
            product_details = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Please make sure you choose the right color and size"}, status=404)

        product.inventory -= quantity
        product.save()

        cart = request.session.get('cart', {})
        
        product_key = f"{product_id}_{size}_{color}"

        
        if product_key in cart:
            cart[product_key]['quantity'] += quantity
            cart[product_key]['added_at'] = timezone.now().isoformat()
        else:
            cart[product_key] = {
                'id': product_id,
                'product_name': product_details.product_name,
                'price': str(Decimal(product_details.price)),
                'is_discount':product_details.is_discount,
                'price_after_discount': str(Decimal(product_details.price_after_discount)) if product_details.price_after_discount is not None else None,
                'quantity': quantity,
                'color': color,
                'size': size,
                'added_at': timezone.now().isoformat()
            }

        request.session['cart'] = cart
        request.session.modified = True
        cart_items = [{'id': item['id'], 'product_name': item['product_name'],
                       'is_discount':item['is_discount'],'price_after_discount':item['price_after_discount'],
                       'price': item['price'], 'quantity': item['quantity'],
                       'color': item['color'], 'size': item['size'],
                       'added_at': item['added_at']}
                      for item in cart.values()]
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveFromCart(APIView):
    """
    Remove a product from the user's cart in the session.

    Methods
    -------
    post(request):
        Removes a specified quantity of a product from the cart, updating inventory and session data.
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        size = request.data.get('size')
        color = request.data.get('color')

        try:
            product = Diversity.objects.get(product_id=product_id,color = color, size=size)
        except Diversity.DoesNotExist:
            return Response({"message": "Product not found."}, status=404)
        
        try:
            product_details = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=404)

        cart = request.session.get('cart', {})
        product_key = f"{product_id}_{size}_{color}"

        if product_key in cart:
            cart_quantity = cart[product_key]['quantity']

            if quantity > cart_quantity:
                return Response({"message": "Cannot remove more than the quantity in the cart."}, status=400)

            cart[product_key]['quantity'] -= quantity

            if cart[product_key]['quantity'] <= 0:
                del cart[product_key]

            product.inventory += quantity
            product.save()

            request.session['cart'] = cart

            cart_items = [{"id": item['id'], 'product_name': item['product_name'],
                           'is_discount':item['is_discount'],'price_after_discount':item['price_after_discount'],
                           'price': item['price'], 'color': item['color'],
                           'size': item['size'], 'quantity': item['quantity']}
                          for item in cart.values()]

            serializer = CartSerializer(cart_items, many=True)
            return Response(serializer.data)

        return Response({"message": "Product not found in cart."}, status=404)


class Delete(APIView):
    """
    Completely remove a product from the user's cart in the session.

    Methods
    -------
    post(request):
        Deletes a specified product from the cart and updates inventory.
    """
    def post(self, request):
        product_id = request.data.get('product_id')
        size = request.data.get('size')
        color = request.data.get('color')

        try:
            product = Diversity.objects.get(product_id=product_id,color = color, size=size)
        except Diversity.DoesNotExist:
            return Response({"message": "Product not found."}, status=404)

        cart = request.session.get('cart', {})
        product_key = f"{product_id}_{size}_{color}"

        if product_key in cart:
            current_quantity = cart[product_key].get('quantity', 0)
            del cart[product_key]

            product.inventory += current_quantity
            product.save()

        request.session['cart'] = cart
        cart_items = [{"id": item['id'], 'product_name': item['product_name'],
                       'is_discount':item['is_discount'],'price_after_discount':item['price_after_discount'],
                       'price': item['price'], 'color': item['color'],
                       'size': item['size'], 'quantity': item['quantity']}
                      for item in cart.values()]

        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)


class TotalPrice(APIView):
    """
    Calculate the total price of items in the cart.

    Methods
    -------
    get(request):
        Returns the total price of all items in the cart, taking discounts into account.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart = request.session.get('cart', {})
        total_price = 0.0
        for item in cart.values():
            print(item["is_discount"])
            if item["is_discount"]==True:
                item_total = float(item["price_after_discount"]) * item["quantity"]
            else:
                item_total = float(item["price"]) * item["quantity"]
            item["total"] = item_total
            total_price += item_total

        return Response(total_price)
    

class ShowCart(APIView):
    """
    Display the current items in the user's cart.

    Methods
    -------
    get(request):
        Retrieves and displays all items currently in the user's cart.
    """
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        cart = request.session.get('cart', {})
        request.session['cart'] = cart
        cart_items = [{'id':item['id'],'product_name': item['product_name'],'is_discount':item['is_discount'],'price_after_discount':item['price_after_discount'], 'price': item['price'], 'color':item['color'],'size':item['size'],'quantity': item['quantity'],'added_at':item['added_at']}
                      for item in cart.values()]
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)
    
class NumberOfProduct(APIView):
    """
    Count the number of distinct products in the user's cart.

    Methods
    -------
    get(request):
        Returns the total number of distinct products in the cart.
    """
    # permission_classes = [IsAuthenticated]
    def get(self,request):
        cart = request.session.get('cart', {})
        request.session['cart'] = cart
        cart_items = [{"id":item['id'],'product_name': item['product_name'],'is_discount':item['is_discount'],'price_after_discount':item['price_after_discount'], 'price': item['price'],'color':item['color'],'size':item['size'],'quantity': item['quantity']}
                      for item in cart.values()]
        return Response(len(cart_items))


