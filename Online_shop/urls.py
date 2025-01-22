from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("MaktabShopAdmin/", admin.site.urls),
    path("", include("Products.urls")),
    path("", include("Orders.urls")),
    path("", include("User.urls")),
    path("", include("Discount.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
