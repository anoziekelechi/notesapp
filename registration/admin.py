from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from registration.models import MyUser


class UserCreationForm(forms.ModelForm):
    password1=forms.CharField(
        label='password',
        widget=forms.PasswordInput(attrs={'placeholder':'Must contain upper case,lower case,digits and special chracters'})
    )
    password2=forms.CharField(label='password confirmation',widget=forms.PasswordInput)


    class Meta:
        model=MyUser
        fields=('first_name','last_name','email')

    def clean_password2(self):
        #check if the two password matches
        password1=self.cleaned_data.get("password1")

        password2=self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError('password mismatch')
        return password2
    def save(self,commit=True):


        user=super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):



    password=ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'is_active')
    def clean_password(self):

        return self.initial["password"]




class Custom_Admin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('personal info',
         {'fields': ('first_name', 'last_name')}),
        ('permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
                }),
    )
    # this form will be used to add users_accounts and change users_accounts instance
    form=UserChangeForm
    add_form = UserCreationForm

    list_display = ('email','first_name','last_name','date_joined','account_confirm_status','is_superuser')


    search_fields = ['email']
    ordering = ['email']
admin.site.register(MyUser,Custom_Admin)




