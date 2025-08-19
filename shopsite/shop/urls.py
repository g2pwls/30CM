from django.urls import path, include
from django.conf import settings
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from shop import views as shop_views
app_name = "shop"
urlpatterns = [
    # path("", shop_views.all_products)
    path("", shop_views.HomeView.as_view(), name="home"),
    # path("shop/", include("shop.urls", namespace="shop")),
    path("<int:pk>", shop_views.ProductDetail.as_view(), name="product_detail"),
    path("search/", views.search, name="search"),
    path('category/<slug:slug>/', shop_views.ProductListByCategory.as_view(), name='product_category'),
    path("category/<slug:category_slug>/<slug:subcategory_slug>/", shop_views.ProductListBySubCategory.as_view(), name="product_subcategory"),
    path(
        "category/<slug:category_slug>/<slug:subcategory_slug>/<slug:nested_subcategory_slug>/",
        shop_views.ProductListByNestedSubCategory.as_view(),
        name="product_nested_subcategory"
    ),
    path('qna/<int:pk>/', include('qna.urls')),  # QnA URL 포함
    path('product/<int:product_id>/toggle_like/', views.toggle_like, name='toggle_like'),
    path('payments/complete/', views.payment_complete, name='payment_complete'),
    path('direct-purchase/<int:product_id>/', views.direct_purchase, name='direct_purchase'),
    path('checkout-selected/', views.checkout_selected, name='checkout_selected'),
    path('checkout/', views.checkout, name='checkout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)