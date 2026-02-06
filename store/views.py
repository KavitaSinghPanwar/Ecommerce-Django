
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Product, ShoeSize, User, CartItem


from .models import (
    User,
    Product,
    ShoeSize,
    Cart,
    CartItem,
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

        request.session["user_id"] = user.id
        request.session["user_email"] = user.email

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
    products = Product.objects.all()

    # SEARCH
    query = request.GET.get("q")
    if query:
        products = products.filter(name__icontains=query)

    # FILTERS
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

    # SORT
    sort = request.GET.get("sort")
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")

    brands = Product.objects.values_list("brand", flat=True).distinct()

    context = {
        "products": products,
        "brands": brands,
        "query": query,
    }

    return render(request, "store/home.html", context)


# ===================== PRODUCT DETAIL =====================

def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    sizes = ShoeSize.objects.filter(product=product).order_by("size")

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "sizes": sizes,
        }
    )


# ===================== ADD TO CART =====================

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


# ===================== CART PAGE =====================

from django.shortcuts import get_object_or_404, redirect
from .models import Cart, CartItem, Product, User

def add_to_cart_view(request, product_id):
    if "user_id" not in request.session:
        return redirect("login")

    user = get_object_or_404(User, id=request.session["user_id"])
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get("size")

    if not size:
        return redirect("product-detail", product_id=product.id)

    # 🔹 Get or create cart
    cart, created = Cart.objects.get_or_create(user=user)

    # 🔹 Add item to cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={"quantity": 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")
