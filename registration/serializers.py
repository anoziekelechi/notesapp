from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import re
from customvalidators.custom_password_validators import name_validator, password_validator
from registration.models import MyUser
def checkname(name):
    name_validator3 = RegexValidator('^[a-zA-Z]+$')
    if name !=name_validator3:
        raise serializers.ValidationError('error')
    return name

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=settings.AUTH_USER_MODEL.objects.all())]
            )
    first_name=serializers.CharField(
        required=True,
        validators=[name_validator]
    )
    last_name=serializers.CharField(required=True,validators=[name_validator])
    password = serializers.CharField(min_length=8,write_only=True,validators=[password_validator])
    password2 = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'first_name','last_name','password')
        # extra_kwargs={
        #     'first_name':{'required':True},
        #     'last_name':{'required':True}
        # }


    # def validate(self,data):
    #     if not re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$', value):
    #         raise serializers.ValidationError('error')
    #
    #     return value

    def validate(self, attrs):
        if attrs['password'] !=attrs['password2']:
            raise serializers.ValidationError({"password":"Password field mismatch"})
        # if not re.findall('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*\W).*$', attrs):
        #     raise serializers.ValidationError({"password": "Password field error"})

        return attrs

    def create(self, validated_data):
        #ab=get_user_model() django contrib.auth
        user = settings.AUTH_USER_MODEL.objects.create_user(
            validated_data['email'],
            validated_data['first_name'],
            validated_data['last_name'],
            validated_data['password']
        )

        # user = settings.AUTH_USER_MODEL.objects.create_user(
        #     email=validated_data['email'],
        #     first_name=validated_data['first_name'],
        #     last_name=validated_data['last_name'],
        #     password=validated_data['password']
        # )
        # user.is_admin=False
        # user.is_staff = False
        # user.account_confirm_status=False
        # user.save()
        return user
    # def create(self, validated_data):
    #     user=settings.AUTH_USER_MODEL.objects.create(
    #         email=validated_data['email'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name']
    #     )
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user

class PasswordChangeSerializer(serializers.Serializer):
    current_pass=serializers.CharField(required=True)
    new=serializers.CharField(required=True,write_only=True)
    def validate_old(self,value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password':'Does not match'})
        return value