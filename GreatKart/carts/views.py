from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product,Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
"""
tạo một giỏ hàng từ session trên website,
kiểm tra nếu không phải giỏ hàng thì khởi tạo,
trả về cart
"""
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

"""
muốn thêm sản phẩm vào giỏ hàng thì truyền request và mã sản phẩm product_id,
chúng ta sẽ lấy sản phẩm theo mã, kiểm tra xem form thêm vào giỏ hàng có phải POST?
nếu phải thì lấy key và value của request sau đó kiểm tra xem thông tin về màu sắc và size áo,
và chúng ta bắt đầu lấy giỏ hàng theo id, nếu giỏ hàng không tồn tại thì tạo cái mới với session

"""
# Thêm hàng vào giỏ hàng
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # lấy sản phẩm
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact= key,variation_value__iexact =value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user =current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,user =current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
        
            if product_variation in ex_var_list:
                # tăng số lượng quality của cart item
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id = item_id)
                item.quality += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quality =1,user=current_user)
                # tạo một cart item mới
                if len(product_variation)> 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            # cart_item.quality += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quality=1,
                user =current_user,
            )
            if len(product_variation)> 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect("cart")
    # nếu như người dùng chưa đăng nhập
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product = product,variation_category__iexact= key,variation_value__iexact =value)
                    product_variation.append(variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(
                cart_id=_cart_id(request)
            )  # lấy giỏ hàng sử dụng cart_id trên session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            """
            có tồn tại variation hay là không -> database
            variation hiện tại -> product_variation
            item_id -> database
            """

            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
        
            if product_variation in ex_var_list:
                # tăng số lượng quality của cart item
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id = item_id)
                item.quality += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quality =1,cart=cart)
                # tạo một cart item mới
                if len(product_variation)> 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            # cart_item.quality += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quality=1,
                cart=cart,
            )
            if len(product_variation)> 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect("cart")


# giảm số lượng sản phẩm
"""
lấy giỏ hàng theo id và trả về 404 nếu không có sản phẩm,
kiểm tra số lượng của sản phẩm nếu lớn hơn 1 thì giảm xuống,
nếu không thì xóa khỏi giỏ hàng và trẻ về đường dẫn trang giỏ hàng
"""
def remove_cart(request, product_id,cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user = request.user, id= cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id= cart_item_id)
        if cart_item.quality > 1:
            cart_item.quality -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")


# xóa sản phẩm khỏi giỏ hàng
"""
lấy giỏ hàng theo id và trả về 404 nếu không có sản phẩm,
lấy ra sản phẩm trong giỏ hàng và xóa, trả về đường dẫn trang giỏ hàng
"""
def remove_cart_item(request, product_id,cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user = request.user,id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect("cart")


# lấy ra giá, tiền hàng và sản phẩm
"""
lấy ra giỏ hàng theo id và filter những sản phẩm có trong giỏ hàng,
total là tiền phải trả theo từng sản phẩm, quality là số lượng sản phẩm, 
tax là tiền thuế, grand_total là tổng tiền phải trả bao gồm thuế,
và sau đó truyền các bieiesn vào trang cart.html
"""
def cart(request, total=0, quality=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user =request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quality
            quality += cart_item.quality
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        "total": total,
        "quality": quality,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "store/cart.html", context)

@login_required(login_url='login')

def checkout(request, total=0, quality=0, cart_items=None):
    """
    kiểm tra xem người dùng đã đăng nhập hay chưa, nếu đã đăng nhập thì lấy mã giỏ hàng
    dựa trên user, không thì lấy mã giỏ hàng ở trên session cách tính tương tự như 
    phần giỏ hàng
    """
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quality)
            quality += cart_item.quality
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total': total,
        'quality': quality,
        'cart_items': cart_items,
        'tax'       : tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)