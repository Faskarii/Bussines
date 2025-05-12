from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def _create_user(self, email, username, first_name, last_name, password=None, is_active=True, **kwargs):
        if not email:
            raise ValidationError("The Email field must be set")
        if not username:
            raise ValidationError("The Username field must be set")
        if not first_name or not last_name:
            raise ValidationError("First name and last name are required")
        if not password:
            raise ValidationError("Password is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, first_name, last_name, password=None, **kwargs):
        kwargs.setdefault('is_staff', False)
        return self._create_user(email, username, first_name, last_name, password, True, **kwargs)

    def create_superuser(self, email, username, first_name, last_name, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self._create_user(email, username, first_name, last_name, password, True, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(default='users/images/default_avatar.png', upload_to='avatars/', null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class InstructorRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.user.is_staff = True
            self.user.save(update_fields=['is_staff'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Instructor request for {self.user.username}"

