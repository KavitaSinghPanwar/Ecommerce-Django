from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),

    # AUTH
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),

    # PRODUCTS & CART
    path("product/<int:product_id>/", views.product_detail_view, name="product-detail"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart_view, name="add-to-cart"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/update/<int:item_id>/<str:action>/", views.update_quantity_view, name="update-quantity"),
    path("cart/remove/<int:item_id>/", views.remove_item_view, name="remove-item"),

    # ORDERS
    path("checkout/", views.checkout_view, name="checkout"),
    path("order-success/", views.order_success_view, name="order-success"),
    path("order/<int:order_id>/", views.order_detail_view, name="order-detail"),

    # ACCOUNT
    path("account/", views.account_view, name="account"),
    path("account/edit/", views.edit_profile_view, name="edit-profile"),

    # ADMIN DASHBOARD
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # STATIC PAGES
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("collection/", views.collection_view, name="collection"),
]
