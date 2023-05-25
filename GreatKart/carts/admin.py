from django.contrib import admin
from .models import Cart,CartItem
# Register your models here.

"""
định dạng hiển thị thông tin trong tran quản trị
"""
class CartAdmin(admin.ModelAdmin):
    list_display =('cart_id','date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display =('product','cart','quality', 'is_active')

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)