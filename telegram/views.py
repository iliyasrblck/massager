from contextlib import redirect_stderr
from django.db.models import OuterRef, Subquery
from django.contrib.auth import logout, login,authenticate
from django.core.mail import send_mail
from django.contrib import messages
from django.template.defaultfilters import first
from django.template.loader import render_to_string
from telegram.forms import *
from .models import Massage, Chat, User
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from random import randint
from django.db.models import Q





#تابع ها
def _otp(email, massages):
    send_mail(
        subject='کد وروود به سایت',
        message=massages,
        from_email= 'ilia.salim.bayati@gmail.com',
        recipient_list = [email]
    )
# Create your views here.


@login_required
def index_views(request):
    chats = Chat.objects.filter(user1=request.user) | Chat.objects.filter(user2 = request.user)

    last_MS = Massage.objects.filter(chat = OuterRef('pk')).order_by('-create_at')
    chats = chats.annotate(last_mas=Subquery(last_MS.values('text')[:1]))

    context = {
        'chats': chats,

    }
    return render(request, 'telegram/chat_lst.html', context)


def logout_views(request):
    logout(request)
    return redirect('/')


def login_views(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('telegram:index')

    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def block_V(request, username):
    other_user = get_object_or_404(User, username=username)

    chat = get_object_or_404(Chat,
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user)
    )

    if request.method == "POST":
        if chat.user1 == request.user :
            chat.user1_blocked_user2 = not chat.user1_blocked_user2
        else:
            chat.user2_blocked_user1 = not chat.user2_blocked_user1
        chat.save()

    return redirect('telegram:privet_chat', username=username)

@login_required
def privet_chat_views(request, username):
    other_user = get_object_or_404(User, username=username)

    chat = Chat.objects.filter(
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user)
    ).first()

    if not chat:
        chat = Chat.objects.create(user1=request.user, user2=other_user)

    if request.method == "POST":
        form = MassageForm(request.POST, request.FILES)  # ← اینجا تغییر دادیم

        if chat.user1 == request.user:
            blocked = chat.user2_blocked_user1
        else:
            blocked = chat.user1_blocked_user2

        if form.is_valid() and not blocked:
            massage = form.save(commit=False)
            massage.chat = chat
            massage.sender = request.user
            massage.save()
            chat.save()

            return JsonResponse({
                "success": True,
                "message": {
                    "id": massage.id,
                    "text": massage.text,
                    "sender": massage.sender.username,
                    "pic_url": massage.pic.url if massage.pic else None,
                    "time": massage.create_at.strftime("%H:%M")
                }
            })
        else:
            return JsonResponse({"success": False, "error": "پیام ارسال نشد"}, status=400)

    else:
        form = MassageForm()

    massages = chat.massage.all()

    context = {
        'form': form,
        'massages': massages,
        'other_user': other_user,
        'chat': chat,
    }
    return render(request, 'telegram/chat.html', context)




def signup_views(request):
    if request.method == "POST":
        form = SingUpForm(request.POST)
        if form.is_valid():
            #ذخیره موقت اطلاعات کاربر
            user_data = form.cleaned_data
            request.session['user_data']={
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': user_data['email'],
                'password1': user_data['password1'],
            }



            otp = randint(100000, 999999)
            masages = render_to_string('email_cod/cod_otp.txt', {"otp": otp})
            request.session['otp'] = otp
            _otp(email=user_data['email'], massages=masages)

            messages.success(request, "کد ورود به ایمیل شما ارسال شد")
            return redirect("telegram:check_otp")

        else:
            if "email" in form.errors:
                    messages.error(request, "این ایمیل وجود دارد لطفا وارد شوید")
                    return redirect("telegram:login")
    else:
        form = SingUpForm()

    return render(request, 'registration/singup.html', context={"form": form})


def check_otp(request):
    if request.method == "POST":
        form =CheackOTP(request.POST)
        if form.is_valid():
            user_otp = form.cleaned_data['otp']
            real_otp = request.session.get('otp')
            user_data = request.session.get('user_data')

            if int(user_otp) == int(real_otp):
                user = User.objects.create_user(
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    password=user_data['password1'],
                )

                del request.session['otp']
                del request.session['user_data']

                messages.success(request, "ثبت‌نام با موفقیت انجام شد")
                return redirect("telegram:login")

            else:
                messages.error(request, "کد وارد شده اشتباه است")
    else:
        form = CheackOTP()

    return render(request, 'registration/check_otp.html', {'form': form})


def write_email_RP_views(request):
    if request.method == "POST":
        form = Email(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None


            if user is None:
                # اگر ایمیل اشتباه بود
                form.add_error("email", "کاربری با این ایمیل وجود ندارد.")
                return render(request, 'registration/reset-passwords/write_email.html', {"form": form})


            otp = randint(100000, 999999)
            request.session['otp'] = otp
            request.session['email'] = email
            masage = render_to_string('email_cod/change_pas.rename', {"otp": otp})
            _otp(email=email, massages=masage)
            return redirect('telegram:password_cod')


    else:
        form = Email()
    context = {
        'form': form,
    }
    return render(request, 'registration/reset-passwords/write_email.html', context)


def cod_otp_RP_views(request):
    if request.method == "POST":
        form =  CheackOTP(request.POST)
        if form.is_valid():
            number = form.cleaned_data['otp']
            user_otp = request.session.get('otp')
            user_email = request.session.get('email')

            if user_otp is None or user_email is None:
                messages.error(request, "ایمیل شما اشتباه هست یا کد منقضی شده است لطفا دوباره تلاش کنید.")
                return redirect("telegram:password_reset")

            if str(user_otp) == str(number):
                user = User.objects.filter(email=user_email).first()
                if not user:
                    messages.error(request, "کاربری با این ایمیل وجود ندارد!")
                    return redirect("telegram:password_reset")

                del request.session['otp']
                del request.session['email']
                request.session['reset_user_id'] = user.id


                return redirect("telegram:password_change")




            else:
                messages.error(request, "کد وارد شده اشتباه است")

    else:
        form = CheackOTP()

    return render(request, 'registration/check_otp.html', {'form': form})


def reset_password_views(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect("telegram:password_reset")
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = ChangePassword(request.POST)
        if form.is_valid():

            pas= form.cleaned_data['password1']
            user.set_password(pas)
            user.save()

            del request.session['reset_user_id']

            messages.success(request, "رمز عبور با موفقیت تقییر کرد")
            return redirect("telegram:login")
    else:
        form = ChangePassword()

    return render(request, 'registration/reset-passwords/change_password.html', {'form': form})


@login_required
def profile_V (request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user,)
        #request.FILES = برای ذخیره شدن فایل ها مثل عکس
        #instance=request.user = برای این که بگیم داریم ویرایش میکنیم  وگرنه فکر میکنه داریم کاربر جدید میسازیم

        if form.is_valid():
            form.save()
            return redirect('telegram:profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'telegram/my_profile.html', {'form': form})


def chat_profile_V(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'user': user,
    }

    return render(request, 'telegram/chat_profile.html', context)

