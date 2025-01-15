from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product, Category, Gallery, Diversity, ProductAttribute
from .serializers import ProductSerializer, CategorySerializer, DiversitySerializer, GallerySerializer, ProductAttributeSerializer
from django.core.cache import cache


class ProductList(APIView):
    """
    API view to retrieve a list of all products.

    Methods
    -------
    get(request, format=None):
        Handles GET requests to return a list of all products,
        optionally filtered by discount.
    """
    def get(self, request, format=None):
        paginate_by = 10
        
        
        is_discount = request.query_params.get('is_discount', None)

        
        if is_discount is not None:
            
            is_discount = is_discount.lower() in ['true', '1', 't']
            products = Product.objects.filter(is_discount=is_discount)
        else:
            products = Product.objects.all()
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class DisversityList(APIView):
    """
    API view to retrieve a list of all product diversities.

    Methods
    -------
    get(request, format=None):
        Handles GET requests to return a list of all diversities.
    """
    def get(self, request, format=None):
        products = Diversity.objects.all()
        serializer = DiversitySerializer(products, many=True)
        return Response(serializer.data)
    

CACHE_TIMEOUT = 90 * 24 * 60 * 60  

class ProductAttributeList(APIView):
    """
    API view to retrieve attributes for a specific product.

    Methods
    -------
    get(request, product_id):
        Handles GET requests to return attributes of a product identified by product_id.
    """
    def get(self, request, product_id):
        cache_key = f'product_attributes_{product_id}'
        data = cache.get(cache_key)

        if data is None:
            data = ProductAttribute.objects.filter(product_id=product_id)
            serializer = ProductAttributeSerializer(data, many=True)
            cache.set(cache_key, serializer.data, timeout=CACHE_TIMEOUT)
            return Response(serializer.data)
        
        return Response(data)


class CategoryList(APIView):
    """
    API view to retrieve a list of all categories.

    Methods
    -------
    get(request, format=None):
        Handles GET requests to return a list of all categories.
    """
    def get(self, request, format=None):
        cache_key = 'category_list'
        data = cache.get(cache_key)

        if data is None:
            data = Category.objects.all()
            serializer = CategorySerializer(data, many=True)
            cache.set(cache_key, serializer.data, timeout=CACHE_TIMEOUT)
            return Response(serializer.data)
        
        return Response(data)


class CategoryItems(APIView):
    """
    API view to retrieve items in a specific category.

    Methods
    -------
    get(request, cat_id):
        Handles GET requests to return items under the category identified by cat_id.
    """
    def get(self, request, cat_id):
        cache_key = f'category_items_{cat_id}'
        data = cache.get(cache_key)

        if data is None:
            data = Category.objects.filter(parent=cat_id)
            serializer = CategorySerializer(data, many=True)
            cache.set(cache_key, serializer.data, timeout=CACHE_TIMEOUT)
            return Response(serializer.data)
        
        return Response(data)


class ProductCat(APIView):
    """
    API view to retrieve products in a specific category.

    Methods
    -------
    get(request, cat_id):
        Handles GET requests to return products in the category identified by cat_id.
    """
    def get(self, request, cat_id):
        cache_key = f'products_in_category_{cat_id}'
        data = cache.get(cache_key)

        if data is None:
            subcat = Category.objects.filter(parent=cat_id)
            data = Product.objects.filter(Q(category=cat_id) | Q(category__parent=cat_id))
            serializer = ProductSerializer(data, many=True)
            cache.set(cache_key, serializer.data, timeout=CACHE_TIMEOUT)
            return Response(serializer.data)
        
        return Response(data)
    
class Product_details(APIView):
    """
    API view to retrieve details of a specific product.

    Methods
    -------
    get(request, product_id):
        Handles GET requests to return details of the product identified by product_id.
    """
    def get(self, request, product_id):
        data = Product.objects.filter(id=product_id)
        serializer = ProductSerializer(data, many=True)
        return Response(serializer.data)
    
class Product_diversity_details(APIView):
    """
    API view to retrieve diversity details for a specific product.

    Methods
    -------
    get(request, product_id):
        Handles GET requests to return diversity information for the product identified by product_id.
    """
    def get(self, request, product_id):
        data = Diversity.objects.filter(product_id=product_id)
        serializer = DiversitySerializer(data, many=True)
        return Response(serializer.data)
    
class GalleryList(APIView):
    """
    API view to retrieve a list of all galleries.

    Methods
    -------
    get(request, format=None):
        Handles GET requests to return a list of all galleries.
    """
    def get(self, request, format=None):
        data = Gallery.objects.all()
        serializer = GallerySerializer(data, many=True)
        return Response(serializer.data)
    
class SearchItems(APIView):
    """
    API view to search for products based on a query.

    Methods
    -------
    get(request):
        Handles GET requests to search for products by name based on the provided query parameter 'q'.
    """
    def get(self, request):
        query = request.GET.get('q', None)
        if query:
            # Perform the search
            products = Product.objects.filter(Q(product_name__icontains=query))
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)