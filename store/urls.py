from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    ##path("admin-dashboard/", views.admin_dashboard, name="admin-dashboard"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),
    path("product/<int:product_id>/", views.product_detail_view, name="product-detail"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart_view, name="add-to-cart"),




]
