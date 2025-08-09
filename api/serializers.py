from rest_framework import serializers
from .models import CustomUser, Post, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
User= get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    owner_username= serializers.ReadOnlyField(source= 'owner.username', read_only= True)

    class Meta:
        model= Comment
        fields= ('id', 'post', 'owner_username', 'text', 'created')
        read_only_fields= ('id', 'owner_username', 'created')


class PostSerializer(serializers.ModelSerializer):
    comments= CommentSerializer(many= True, read_only= True)
    likes_count= serializers.IntegerField(source= 'liked_by.count', read_only= True)
    owner= serializers.ReadOnlyField(source= 'owner.username')

    class Meta:
        model= Post
        fields= ['id', 'owner', 'text', 'picture', 'comments', 'likes_count', 'created']
        read_only_fields= ['id', 'owner', 'created']

    def validate(self, attrs):
        text= attrs.get('text', '').strip()
        picture= attrs.get('picture', None)
        if not text and not picture:
            raise serializers.ValidationError('Post can not be empty')
        return attrs


class UserRegisterSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only= True, min_length=  8,
    validators= [validate_password], style= {'input_type': 'password'})

    class Meta:
        model= User
        fields= ('name', 'username', 'bio', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)