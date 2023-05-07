from typing import Optional
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):




    def create_user(self, first_name,last_name, username,email, password,**other_fields):


        if not email:
            raise ValueError(_('You must provide an email address'))
        if not username:
            raise ValueError(_('User must have an username'))
        user = self.model(        
        email = self.normalize_email(email),
        username = username,
        first_name = first_name,
        last_name = last_name,
        **other_fields)


        user.set_password(password)
        user.save()
        return user
   
    def create_superuser(self, first_name,last_name, username,email, password,**other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superadmin', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_admin', True)      
   
        return self.create_user(first_name,last_name, username,email, password,**other_fields)
class Account(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)


    # required
    last_login = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin  = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    objects = MyAccountManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']


    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return self.is_admin
   
    def has_module_perms(self, app_label):
        return True
