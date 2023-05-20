from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


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
            user activation
            """
            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string('accounts/account_variation_mail.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            messages.success(request, 'Registration successfull.')
            return redirect('register')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html',context)

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request,user)
            # messages.success(request,"You are now login")
            return redirect('home')
        else:
            messages.error(request,"Invalid login ")
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')

def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')