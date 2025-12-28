from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Post, Comment, Like, Follow, Block
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
User= get_user_model()


class CommentSerializer(ModelSerializer):
    owner_username= serializers.ReadOnlyField(source= 'owner.username')
    likes_count= serializers.IntegerField(read_only= True)
    is_following= serializers.BooleanField(read_only= True)

    class Meta:
        model= Comment
        fields= ['id', 'owner_username', 'text', 'likes_count', 'is_following', 'created_at']
        read_only_fields= ['created_at']


class UserSerializer(ModelSerializer):
    is_following= serializers.BooleanField(read_only= True)

    class Meta:
        model= User
        fields= ['id', 'is_private', 'name', 'username', 'bio', 'is_following']


class PostSerializer(ModelSerializer):
    owner_username= serializers.ReadOnlyField(source= 'owner.username')
    is_private= serializers.ReadOnlyField(source= 'owner.is_private')
    is_following= serializers.BooleanField(read_only= True)
    comments_count= serializers.IntegerField(read_only= True)
    likes_count= serializers.IntegerField(read_only= True)

    class Meta:
        model= Post
        fields= ['id', 'is_private', 'owner_username', 'is_following', 'picture', 'text', 'likes_count', 'comments_count', 'created_at']
        read_only_fields= ['owner_username', 'created_at']

    def validate(self, attrs):
        text= attrs.get('text', '').strip()
        picture= attrs.get('picture', None)
        if not text and not picture:
            raise serializers.ValidationError('Post can not be empty')
        return attrs


username_validator= RegexValidator(
    regex= r'^[\w.@+-]+$',
    message= 'Username can only contain letters, numbers and @/./+/-/_ characters (no spaces).'
)

class UserRegisterSerializer(ModelSerializer):
    username= serializers.CharField(validators= [username_validator])
    password= serializers.CharField(write_only= True, min_length= 8,
    validators= [validate_password], style= {'input_type': 'password'})

    class Meta:
        model= User
        fields= ['id', 'name', 'username', 'bio', 'is_private', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class FollowSerializer(ModelSerializer):
    follower= serializers.ReadOnlyField(source= 'follower.username')
    following= serializers.ReadOnlyField(source= 'following.username')
    class Meta:
        model= Follow
        fields= ['id', 'follower', 'following', 'is_accepted', 'created_at']
        read_only_fields= ['created_at']


class BlockSerializer(ModelSerializer):
    blocker= serializers.ReadOnlyField(source= 'blocker.username')
    blocking= serializers.ReadOnlyField(source= 'blocking.username')

    class Meta:
        model= Block
        fields= ['id', 'blocker', 'blocking', 'created_at']