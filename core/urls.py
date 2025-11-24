from django.urls import path
from shop import views as shop_views
app_name = "core"
urlpatterns = [
    # path("", shop_views.all_products)
    path("", shop_views.HomeView.as_view(), name="home")
]