from django import forms
from .models import Massage, User
from django.contrib.auth import authenticate


class MassageForm(forms.ModelForm):
    class Meta:
        model = Massage
        fields = ['text','pic']

class SingUpForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز',max_length=20,  widget=forms.PasswordInput())
    password2 = forms.CharField(label='تکرار رمز', max_length=20, widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError("پسورد ها یکی نیست")
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("این ایمیل قبلاً ثبت شده است. لطفاً وارد شوید.")
        return email

class CheackOTP(forms.Form):
    otp = forms.CharField(label='کد ارسال شده را وارد کنید')

class Email(forms.Form):
    email = forms.EmailField(label='ایمیل خود را وارد کنید')

class ChangePassword(forms.Form):
    password1 = forms.CharField(label='رمز عبور', widget=forms.PasswordInput())
    password2 = forms.CharField(label='تکرار رمز', widget=forms.PasswordInput())
    def clean_password2(self):
        cd = self.cleaned_data
        pas1 = cd.get('password1')
        pas2 = cd.get('password2')
        if pas1 and pas2 and pas1 != pas2:
            raise forms.ValidationError("پسورد ها یکی نیست!!!")
        return pas2

class LoginForm(forms.Form):
    username = forms.CharField(label='ایمیل یا یوزر نیم')
    password = forms.CharField(label='رمز عبور', widget=forms.PasswordInput())
    user =None

    def clean(self):
        clean_data = super().clean()
        username_or_email = clean_data.get('username')
        password = clean_data.get('password')

        if username_or_email and password:

            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    username = user_obj.username
                except User.DoesNotExist:
                    raise forms.ValidationError("ایمیل یا نام کاربری اشتباه است")
            else:
                username = username_or_email

            # انجام لاگین Django
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("نام کاربری یا رمز عبور اشتباه است")

            # ذخیره کاربر واقعی
            self.user = user

        return clean_data

    def get_user(self):
        return getattr(self, 'user', None)

class EditProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )
    class Meta:
        model = User
        fields = ['photo_profile','username','first_name', 'last_name', 'email','phone_number','birth_date' ]

