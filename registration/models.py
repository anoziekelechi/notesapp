from django.db import models

# Create your models here.

import hashlib
import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse

from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from customvalidators.custom_password_validators import email_validator, name_validator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, first_name, last_name,password=None):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,

        )
        user.set_password(password)#from official docs
        user.save(using=self._db)
        return user


    def create_superuser(self,first_name,last_name, email,password=None):
        user=self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,

        )
        user.is_superuser=True
        user.is_staff=True
        user.save(using=self._db)

        return user




class MyUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(
        verbose_name='email address',
        blank=False,
        unique=True,
        max_length=70,
        validators=[email_validator],
        error_messages={
            'unique': 'sorry this email is no longer available',
        }

    )
    first_name = models.CharField(
        verbose_name='first name',
        max_length=30,
        blank=False,
        validators=[name_validator],
    )
    last_name = models.CharField(
        verbose_name='last name',
        max_length=30,
        blank=False,
        validators=[name_validator],
    )


    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='make this user a staff of this org',
    )
    is_superuser = models.BooleanField(
        default=False
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    account_confirm_status=models.BooleanField(
        default=False
    )
    contact = PhoneNumberField(null=True,blank=True,verbose_name='Mobile Number')
    date_confirmed = models.DateTimeField(null=True,blank=True)
    avatar_hash = models.CharField(max_length=300,null=True)




    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):  # (self,force_insert=False,force_update=False)
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        self.email = self.email.lower()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        return super(MyUser, self).save(*args, **kwargs)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_absolute_url(self):
        return reverse('password',kwargs={'pk': self.pk})








