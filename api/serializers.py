from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import CustomUser, Post, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
User= get_user_model()


class CommentSerializer(ModelSerializer):
    owner_username= serializers.ReadOnlyField(source= 'owner.username', read_only= True)
    likes_count= serializers.IntegerField(source= 'liked_by.count', read_only= True)

    class Meta:
        model= Comment
        fields= ('id', 'post', 'owner_username', 'text', 'likes_count', 'created')


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= Comment
        fields= ('id', 'text')


class UserSerializer(ModelSerializer):
    is_following= serializers.SerializerMethodField()

    class Meta:
        model= User
        fields= ('id', 'name', 'username', 'bio', 'is_following')
    
    def get_is_following(self, obj):
        request= self.context.get('request')
        if not request:
            return False
        return obj.followed_by.filter(follower= request.user).exists()


class PostSerializer(ModelSerializer):
    owner_username= serializers.CharField(source= 'owner.username') and serializers.ReadOnlyField(source= 'owner.username')
    is_following= serializers.SerializerMethodField()
    likes_count= serializers.IntegerField(source= 'liked_by.count', read_only= True)
    comments_count= serializers.IntegerField(read_only= True)

    def get_is_following(self, obj):
        request= self.context.get('request')
        if not request:
            return False
        return obj.owner.followed_by.filter(follower= request.user).exists()

    class Meta:
        model= Post
        fields= ['id', 'owner_username', 'is_following', 'picture', 'text', 'likes_count', 'comments_count', 'created']
        read_only_fields= ['id', 'owner', 'created', 'likes_count', 'comments_count', 'comments']

    def validate(self, attrs):
        text= attrs.get('text', '').strip()
        picture= attrs.get('picture', None)
        if not text and not picture:
            raise serializers.ValidationError('Post can not be empty')
        return attrs


class UserRegisterSerializer(ModelSerializer):
    password= serializers.CharField(write_only= True, min_length= 8,
    validators= [validate_password], style= {'input_type': 'password'})

    class Meta:
        model= User
        fields= ('id', 'name', 'username', 'bio', 'password')
        read_only_fields= ('id',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)