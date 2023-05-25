from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart,CartItem
from carts.views import _cart_id

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

# Create your views here.
def register(request):
    """
        kiểm tra form bắt method = POST thì sau đó gán giá trị thuộc tính lần lượt
        sau đó sử dụng hàm createuser ở models để gán giá trị và lưu lại thông tin người dùng
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()

            # user activation
            """
            user activation by send the link to this email address,
            then user click into the link below to activate the email
            """
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # messages.success(request, 'Registration successfull.')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    """
    lấy giá trị từ form post của người dùng nếu người dùng không none, 
    chúng ta sẽ cho đăng nhập sau đó kiểm tra giỏ hàng của người dùng
    xem họ có sản phẩm trong giỏ hàng không, sau đó tìm xem nếu mã người dùng đúng
    thì thêm dữ liệu vào
    còn nếu none thì in ra thông báo lỗi và trả về trang login
    """
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # lấy thuộc tính màu và kích cỡ của sản phẩm
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                
                    # lấy sản phẩm của user dựa vào thuộc tính màu và kích cỡ trong giỏ người dùng
                    cart_item = CartItem.objects.filter(user =user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    # product_variation = [1,2,3,4,6]
                    # ex_var_list = [4,6,3,5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quality += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request,user)
            messages.success(request,"You are now login")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # print("query-> ",query)
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)                
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request,"Invalid login ")
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')

def logout(request):
    """
    cho user logout bằng hàm có sẵn trong thư viện auth cùng với thông báo
    You are logged out và trở về trang đăng nhập
    """
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')

def activate(request,uidb64,token):
    """
    kích hoạt tài khoản để người dùng có thể đăng nhập bằng cách đưa uid của người dùng
    nếu người dùng có thì ta tạo ra token và cho kích hoạt, hiển thị thông báo
    và trở về trang login,
    còn nếu không thì ta thông báo là link này không đúng và đưa về trang đăng ký
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
  
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register') 
    
@login_required(login_url = 'login')
def dashboard(request):
  return render(request,  'accounts/dashboard.html')

def forgotPassword(request):
    """
    lấy gmail từ form gửi của người dùng sau đó lấy link trang hiện tại,
    bắt đầu gửi mail cho người dùng để xác nhận, khi người dùng mở mail và nhấn 
    vào đường dẫn thì đưa họ về trang reset mật khẩu nếu email đó tồn tại
    không thì đưa ra lỗi là tài khoản không tồn tại
    """
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact = email)
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            
            messages.success(request,"Password reset email has been sent to your email address.")
            return redirect('login')
        else:
            messages.error(request,"Account does not exists")
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

"""
bắt đầu lấy người dùng theo uid nếu có thông tin người dùng thì 
ta bắt đầu check token rồi đưa ra thông tin cho họ đổi mật khẩu
trả về httpresponse ok
"""
def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('resetPassword')
    else:
        messages.error(request, "This link has ben expired!")
    return HttpResponse("OK")

"""
lấy mật khẩu từ form reset password rồi so sánh
password và confirm_password, nếu trùng thì lưu
không thì hiển thị rằng xác nhận mật khẩu không đúng
"""
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful!')
            return redirect('login')
        else:
            messages.error(request,"Password dose not match!")
            return redirect('resetPassword')
    else:
        return render(request,"accounts/resetPassword.html")