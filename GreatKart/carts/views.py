from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# Thêm hàng vào giỏ hàng
def add_cart(request,product_id):
    product = Product.objects.get(id =product_id) # lấy sản phẩm
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) # lấy giỏ hàng sử dụng cart_id trên session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product = product, cart = cart)
        cart_item.quality += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quality = 1,
            cart = cart,
        )
        cart_item.save()
    return redirect('cart')

# giảm số lượng sản phẩm
def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product = product, cart = cart)
    if cart_item.quality > 1:
        cart_item.quality -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

# xóa sản phẩm khỏi giỏ hàng
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product = product, cart = cart)
    cart_item.delete()
    return redirect('cart')

# lấy ra giá, tiền hàng và sản phẩm
def cart(request, total =0, quality = 0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart = cart, is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price* cart_item.quality)
            quality += cart_item.quality
        tax  = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context ={
        'total': total,
        'quality': quality,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request,'store/cart.html',context)