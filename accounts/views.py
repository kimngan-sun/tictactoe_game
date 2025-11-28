from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import user_not_authenticated

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.db.models.query_utils import Q
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

# Create your views here.

def sendgrid_email(to_email, subject, html_content):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,   # dùng 'to_emails' cho SendGrid >=6.x
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        print("SENDGRID_API_KEY:", settings.SENDGRID_API_KEY)
        print("To Email:", to_email)
        response = sg.send(message)
        if response.status_code in [200, 202]:
            return True
        else:
            print("SendGrid returned status:", response.status_code)
            return False
    except Exception as e:
        print("SendGrid Error:", e)
        return False
    
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Bạn đã đăng ký thành công')
        return redirect('login')
    else:
        messages.error(request,'Link kích hoạt đã vô hiệu hóa')
    return redirect('menu')

def activateEmail(request, user, to_email):
    subject = 'KÍCH HOẠT TÀI KHOẢN'
    html_content = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    if sendgrid_email(to_email, subject, html_content):
        messages.success(request, f'Gửi email kích hoạt đến {to_email} thành công.')
    else:
        messages.error(request, f'Không thể gửi email đến {to_email}')

@user_not_authenticated
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('registration_pending')
        
        else:
            for error in list(form.errors.values()):
                print(request, error)
                messages.error(request, error)
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def registration_pending(request):
    return render(request, 'accounts/registration_pending.html')

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất thành công")
    return redirect('login')

def user_not_authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('menu')  # nếu đã login, vào menu
        return view_func(request, *args, **kwargs)
    return wrapper

@user_not_authenticated
def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Xin chào <b>{user.username}</b>! Bạn đã đăng nhập")
                return redirect("menu")
        else:
            for key, error in form.errors.items():
                if key == 'captcha' and error[0] == 'Trường này là yêu cầu bắt buộc':
                    messages.error(request, 'Bạn phải xác nhận ReCaptcha')
                    continue

                messages.error(request, error) 
    form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def profile(request, username):
    if request.method == 'POST':
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username},Profile của bạn đã được update')
            return redirect('profile', user_form.username)
        for error in list(form.errors.values()):
            messages.error(request, error) 

            
    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        return render(request, 'accounts/profile.html', {'form': form})
    
    return redirect('menu')

@login_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password của bạn đã thay đổi.')
            return redirect('menu')
        else:
            print(form.errors)
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form':form})

@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = 'YÊU CẦU ĐẶT LẠI MẬT KHẨU'
                html_content = render_to_string('template_reset_password.html', {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    'protocol': 'https' if request.is_secure() else 'http'
                })

                if sendgrid_email(associated_user.email, subject, html_content):
                    messages.success(request,
                        "Đã gửi hướng dẫn đặt lại mật khẩu đến email của bạn. "
                        "Nếu không nhận được email, hãy kiểm tra thư mục spam."
                    )
                else:
                    messages.error(request,'Gặp sự cố khi gửi email, vui lòng thử lại sau.')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form':form})

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Mật khẩu của bạn đã được đặt. Bạn có thể <b>đăng nhập</b> ngay bây giờ.')
                return redirect('menu')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Liên kết đã hết hạn!!")

    messages.error(request, 'Đã xảy ra sự cố, đang chuyển hướng về Trang Chủ')
    return redirect('menu')