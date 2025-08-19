from django.urls import path, include
from . import views
app_name = "users"
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("login/email/", views.LoginWithEmailView.as_view(), name="login_email"),
    path("login/email/join/", views.JoinWithEmailView.as_view(), name="join_email"),
    path("validate-email/", views.validate_email, name="validate_email"),
    path("store-session-data/", views.store_session_data, name="store_session_data"),
    path('signup-complete/', views.signup_complete, name='signup_complete'),
    path("logout/", views.log_out, name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/", include("allauth.urls")),
    path('mypage/', views.MypageView.as_view(), name="mypage"),
    path('update/', views.UpdateUserView.as_view(), name="update"),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/str:username/', views.user_profile, name='user_profile'),

    path('shopping-info/', views.shopping_info, name='shopping_info'),
    path('product-reviews/', views.product_reviews, name='product_reviews'),
    path('product-qna/', views.product_qna, name='product_qna'),
    path("like-products/", views.like_products, name="like_products")
]