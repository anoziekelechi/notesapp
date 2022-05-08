from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from home.models import Note
# class CreateNoteSerializer(serializers.ModelSerializer):
#     heading=serializers.CharField(
#         required=True,
#         validators=[UniqueValidator(queryset=Note.objects.all())]
#     )
#     class Meta:
#         model=Note
#         fields=['heading','body']

class NoteSerializer(serializers.ModelSerializer):
    owner=serializers.ReadOnlyField(source='owner.email')
    heading=serializers.CharField(required=True,validators=[UniqueValidator(queryset=Note.objects.all)])
    #body=serializers.CharField(required=True)

    class Meta:
        model=Note
        fields=['id','slug','heading','body','created','updated','owner']
        extra_kwargs={
            'body':{'required':True}
            #'body': {'required': True,validators=[]}
        }
        #validators=[]
