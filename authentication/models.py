from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'