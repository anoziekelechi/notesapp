import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from rest_framework import serializers

name_validator = RegexValidator('^[a-zA-Z]+$', 'Must not contain numbers or special characters')
password_validator = RegexValidator('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$',
                                  'must contain atleast one upper case letters,one lower case letters, one digits and special characters'
                                  )
email_validator = EmailValidator(message='please enter a valid email')
fullname = RegexValidator('^[a-zA-Z\s]+$', 'Must not contain numbers or special characters')



class User_Password_Validation(object):
    def validate(self,password,user=None):
        if not re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$',password):
            raise serializers.ValidationError(
                'Your password must contain an upper case,lower case letters,numbers and special characters',
                code='incorrect'
            )

    def get_help_text(self):
        return 'Your password must contain an upper case,lower case letters,numbers and special characters',

#
# class Passval:
#     def __init__(self,passw):
#         self.passw=passw
#     def __call__(self,value):
#         if re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$') !=passw:
#             message='password in wrong format'
#             raise serializers.ValidationError(message)



class passw2(object):
    def __init__(self,passw):
        self.passw=re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$')

    def __call__(self,value):
        if value != self.passw:
            message = 'password in wrong format'
            raise serializers.ValidationError(message)
       # return value



####
name_validator3 = RegexValidator('^[a-zA-Z]+$')

def checkname(name):
    name_validator3 = RegexValidator('^[a-zA-Z]+$')
    if name !=name_validator3:
        raise serializers.ValidationError('error')
    return name
