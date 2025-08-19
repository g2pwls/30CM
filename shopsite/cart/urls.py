from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', views.add_cart, name='add_cart'),
    path('minus/<int:product_id>/', views.minus_cart, name='minus_cart'),
    path('', views.cart_detail, name='cart_detail'),
    path('delete_item/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('delete_selected/', views.delete_selected_items, name='delete_selected_items'),
]