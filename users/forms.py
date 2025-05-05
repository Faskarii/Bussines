from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


# class SignUpForm(UserCreationForm):
#     username = forms.CharField(
#         error_messages={
#             'required': 'نام کاربری الزامی است',
#             'unique': 'این نام کاربری قبلاً استفاده شده است',
#             'invalid': 'نام کاربری نامعتبر است'
#         }
#     )
#
#     email = forms.EmailField(
#         error_messages={
#             'required': 'ایمیل الزامی است',
#             'invalid': 'لطفاً یک ایمیل معتبر وارد کنید',
#             'unique': 'این ایمیل قبلاً ثبت شده است'
#         }
#     )
#
#     password1 = forms.CharField(
#         widget=forms.PasswordInput,
#         error_messages={
#             'required': 'رمز عبور الزامی است',
#         }
#     )
#
#     password2 = forms.CharField(
#         widget=forms.PasswordInput,
#         error_messages={
#             'required': 'تکرار رمز عبور الزامی است',
#         }
#     )
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        error_messages={
            'required': 'نام کاربری الزامی است',
            'unique': 'این نام کاربری قبلاً استفاده شده است',
            'invalid': 'نام کاربری نامعتبر است'
        }
    )

    email = forms.EmailField(
        error_messages={
            'required': 'ایمیل الزامی است',
            'invalid': 'لطفاً یک ایمیل معتبر وارد کنید',
            'unique': 'این ایمیل قبلاً ثبت شده است'
        }
    )

    first_name = forms.CharField(
        required=True,
        error_messages={
            'required': 'نام الزامی است'
        }
    )

    last_name = forms.CharField(
        required=True,
        error_messages={
            'required': 'نام خانوادگی الزامی است'
        }
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'رمز عبور الزامی است',
        }
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'تکرار رمز عبور الزامی است',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except ValidationError as e:
            raise ValidationError('رمز عبور باید حداقل 8 کاراکتر و شامل حروف و اعداد باشد')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('رمز عبور و تکرار آن باید یکسان باشند')
        return password2

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     if commit:
    #         user.save()
    #     return user
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        error_messages={
            'required': 'نام کاربری الزامی است'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={
            'required': 'رمز عبور الزامی است'
        }
    )