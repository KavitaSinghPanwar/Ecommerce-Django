# ===================== IMPORTS =====================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    User,
    Product,
    ShoeSize,
    Cart,
    CartItem,
    Order,
    OrderItem,
)

# ===================== AUTH =====================

def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "All fields are required")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Account already exists")
            return redirect("signup")

        User.objects.create(
            email=email,
            password=make_password(password)
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "store/signup.html")


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from .models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password required")
            return redirect("login")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("login")

        if not check_password(password, user.password):
            messages.error(request, "Wrong password")
            return redirect("login")

        # ✅ Store session
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        
        # ✅ Add voice flag
        request.session["voice_login"] = True

        return redirect("home")

    return render(request, "store/login.html")



def logout_view(request):
    request.session.flush()
    return redirect("login")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered")
            return redirect("forgot-password")

        user.password = make_password(new_password)
        user.save()

        messages.success(request, "Password updated. Please login.")
        return redirect("login")

    return render(request, "store/forgot_password.html")


# ===================== HOME =====================

def home_view(request):
    # 🔊 Get voice flag safely
    voice = request.session.pop("voice_login", False)

    products = Product.objects.all()

    query = request.GET.get("q")
    if query:
        products = products.filter(name__icontains=query)

    gender = request.GET.get("gender")
    brand = request.GET.get("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if gender:
        products = products.filter(gender=gender)
    if brand:
        products = products.filter(brand=brand)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort")
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    brands = Product.objects.values_list("brand", flat=True).distinct()

    # 🛒 Cart count
    cart_count = 0
    user_id = request.session.get("user_id")
    if user_id:
        cart = Cart.objects.filter(user_id=user_id).first()
        if cart:
            cart_count = CartItem.objects.filter(cart=cart).count()

    return render(request, "store/home.html", {
        "products": products,
        "brands": brands,
        "query": query,
        "cart_count": cart_count,
        "voice_login": voice,   # ✅ IMPORTANT
    })

# ===================== PRODUCT =====================

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = ShoeSize.objects.filter(product=product).order_by("size")

    return render(request, "store/product_detail.html", {
        "product": product,
        "sizes": sizes,
    })


# ===================== CART =====================

def add_to_cart_view(request, product_id):
    if not request.session.get("user_id"):
        return redirect("login")

    if request.method != "POST":
        return redirect("home")

    size = request.POST.get("size")
    if not size:
        messages.error(request, "Please select a shoe size")
        return redirect("product-detail", product_id=product_id)

    user = User.objects.get(id=request.session["user_id"])
    product = get_object_or_404(Product, id=product_id)
    shoe_size = get_object_or_404(ShoeSize, product=product, size=size)

    if shoe_size.stock <= 0:
        messages.error(request, "Selected size is out of stock")
        return redirect("product-detail", product_id=product_id)

    cart, _ = Cart.objects.get_or_create(user=user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
    )

    if not created:
        item.quantity += 1
    item.save()

    messages.success(request, "Added to cart successfully")
    return redirect("cart")


def cart_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    cart = Cart.objects.filter(user_id=user_id).first()
    items = CartItem.objects.filter(cart=cart) if cart else []

    total_price = sum(item.product.price * item.quantity for item in items)

    return render(request, "store/cart.html", {
        "items": items,
        "total_price": total_price,
    })


def update_quantity_view(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect("cart")


def remove_item_view(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, "Item removed from cart")
    return redirect("cart")


# ===================== CHECKOUT & ORDERS =====================

def checkout_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    cart = Cart.objects.filter(user_id=user_id).first()
    if not cart:
        return redirect("cart")

    items = CartItem.objects.filter(cart=cart)
    if not items.exists():
        return redirect("cart")

    total_price = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":
        order = Order.objects.create(
            user_id=user_id,
            total_amount=total_price
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.price
            )

        items.delete()
        cart.delete()

        return redirect("order-success")

    return render(request, "store/checkout.html", {
        "items": items,
        "total_price": total_price,
    })


def order_success_view(request):
    return render(request, "store/order_success.html")


def order_detail_view(request, order_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    order = Order.objects.get(id=order_id, user_id=user_id)
    items = OrderItem.objects.filter(order=order)

    return render(request, "store/order_detail.html", {
        "order": order,
        "items": items,
    })


# ===================== ACCOUNT =====================

def account_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user).order_by("-created_at")

    total_spent = orders.aggregate(total=Sum("total_amount"))["total"] or 0

    return render(request, "store/account.html", {
        "user": user,
        "orders": orders,
        "total_spent": total_spent,
    })


def edit_profile_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if email:
            user.email = email
        if password:
            user.password = make_password(password)

        user.save()
        return redirect("account")

    return render(request, "store/edit_profile.html", {"user": user})


# ===================== ADMIN DASHBOARD =====================

@staff_member_required(login_url="/admin/login/")
def admin_dashboard(request):
    today = now().date()

    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(created_at__date=today).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_products = Product.objects.count()
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]

    return render(request, "store/admin_dashboard.html", {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "today_orders": today_orders,
        "today_revenue": today_revenue,
        "total_products": total_products,
        "recent_orders": recent_orders,
    })


# ===================== STATIC PAGES =====================

def about_view(request):
    return render(request, "store/about.html")


def contact_view(request):
    if request.method == "POST":
        messages.success(request, "Thank you for contacting us. We will get back to you soon.")
    return render(request, "store/contact.html")


def collection_view(request):
    products = Product.objects.all()

    query = request.GET.get("q")
    if query:
        products = products.filter(name__icontains=query)

    gender = request.GET.get("gender")
    brand = request.GET.get("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if gender:
        products = products.filter(gender=gender)
    if brand:
        products = products.filter(brand=brand)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort")
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    brands = Product.objects.values_list("brand", flat=True).distinct()

    return render(request, "store/collection.html", {
        "products": products,
        "brands": brands,
    })
def home(request):
    voice = request.session.pop("voice_login", False)
    return render(request, "store/home.html", {"voice_login": voice})
