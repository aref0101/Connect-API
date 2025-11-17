from rest_framework.viewsets import ModelViewSet
from .models import Post, Comment, Follow
from .serializers import PostSerializer, UserRegisterSerializer, CommentSerializer, CommentCreateSerializer, UserSerializer
from rest_framework import generics, permissions, viewsets, status
from .customPermission import IsOwnerOrReadOnly, IsMeOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
User= get_user_model()
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.db import transaction


class PostViewSet(ModelViewSet):
    serializer_class= PostSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly] 

    @action(detail= True, methods= ['post'], permission_classes= [permissions.IsAuthenticated])
    def togglelike(self, request, pk= None):
        post= self.get_object()
        user= request.user
        if post.liked_by.filter(pk= user.pk).exists():
            post.liked_by.remove(user)
            return Response({'detail': 'unliked', 'likes_count': post.liked_by.count()}, status= status.HTTP_200_OK)
        else:
            post.liked_by.add(user)
            return Response({'detail': 'liked', 'likes_count': post.liked_by.count()}, status= status.HTTP_201_CREATED)

    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def bookmark(self, request, pk= None):
        user= request.user
        target= self.get_object()
        if target.bookmarked_by.filter(pk= user.pk).exists():
            target.bookmarked_by.remove(user)
            return Response({'detail': 'unbookmarked'}, status= status.HTTP_200_OK)
        else:
            target.bookmarked_by.add(user)
            return Response({'detail': 'bookmarked'}, status= status.HTTP_201_CREATED)
        
    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)

    def get_queryset(self):
        return Post.objects.all().annotate(comments_count= Count('comments')).order_by('-created')
    

class BookmarkAPIView(generics.ListAPIView, generics.RetrieveAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(bookmarked_by= self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class= UserRegisterSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset= Comment.objects.all().order_by('-created')
    serializer_class= CommentSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def togglelike(self, request, pk= None):
        user= request.user
        comment= self.get_object()
        if comment.liked_by.filter(pk= user.pk).exists():
            comment.liked_by.remove(user)
            return Response({'detail': 'unliked', 'likes_count': comment.liked_by.count()}, status= status.HTTP_200_OK)
        else:
            comment.liked_by.add(user)
            return Response({'detail': 'liked', 'likes_count': comment.liked_by.count()}, status= status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


class UserViewSet(ModelViewSet):
    queryset= User.objects.all()
    serializer_class= UserSerializer
    permission_classes= [permissions.IsAuthenticated, IsMeOrReadOnly]
    http_method_names= ['get', 'put', 'patch', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Creating user is not allowed in this path'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def followers(self, request, pk= None):
        target= self.get_object()
        qs= User.objects.filter(follows__following= target).distinct()
        serializer= self.get_serializer(qs, many= True)
        return Response(serializer.data)
    
    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def following(self, request, pk= None):
        target= self.get_object()
        qs= User.objects.filter(followed_by__follower= target).distinct()
        serializer= self.get_serializer(qs, many= True)
        return Response(serializer.data)
    
    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def togglefollow(self, request, pk= None):
        user= request.user
        target= self.get_object()
        if user== target:
            return Response({'detail': 'you cannot follow yourself'}, status= status.HTTP_400_BAD_REQUEST)
        elif Follow.objects.filter(follower= user, following= target).exists():
            Follow.objects.filter(follower= user, following= target).delete()
            return Response({'detail': 'unfollowed'}, status= status.HTTP_200_OK)
        else:
            Follow.objects.create(follower= user, following= target)
            return Response({'detail': 'followed'}, status= status.HTTP_201_CREATED)
    

class FollowingPostList(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        user= self.request.user
        following_ids= Follow.objects.filter(follower= user).values_list('following_id', flat= True)
        qs= Post.objects.filter(owner_id__in= following_ids).order_by('-created')
        return qs