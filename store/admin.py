
from django.contrib import admin
from .models import Product, ShoeSize, User

# -------- INLINE SIZE --------
class ShoeSizeInline(admin.TabularInline):
    model = ShoeSize
    extra = 6  # shows 6 size rows by default

# -------- PRODUCT ADMIN --------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "gender", "price")
    list_filter = ("brand", "category", "gender")
    search_fields = ("name", "brand")
    inlines = [ShoeSizeInline]

# -------- USER ADMIN --------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at")
