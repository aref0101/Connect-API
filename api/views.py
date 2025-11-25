from rest_framework.viewsets import ModelViewSet
from .models import Post, Comment, Follow
from .serializers import PostSerializer, CommentSerializer, UserRegisterSerializer, UserSerializer
from rest_framework import generics, permissions, viewsets, status
from .customPermission import IsOwnerOrReadOnly, IsMeOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
User= get_user_model()
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Exists, OuterRef
from rest_framework.pagination import CursorPagination
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound


class SocialPangination(CursorPagination):
    page_size= 10
    ordering= '-created_at'
    cursor_query_param= 'cursor'


class PostViewSet(ModelViewSet):
    serializer_class= PostSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly] 
    pagination_class= SocialPangination

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
        user= self.request.user
        is_following_query= Follow.objects.filter(follower= user, following= OuterRef('owner'))

        return Post.objects.all().select_related('owner').annotate(
            is_following= Exists(is_following_query),
            likes_count= Count('liked_by', distinct= True),
            comments_count= Count('comments', distinct= True),
        )
    

class BookmarkAPIView(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= SocialPangination

    def get_queryset(self):
        return Post.objects.select_related('owner').annotate(
            likes_count= Count('liked_by', distinct= True),
            comments_count= Count('comments', distinct= True)
            ).filter(bookmarked_by= self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class= UserRegisterSerializer


class CommentViewSet(ModelViewSet):
    serializer_class= CommentSerializer
    permission_classes= [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class= SocialPangination

    def get_queryset(self):
        post_pk= self.kwargs.get('post_pk')
        if post_pk is None:
            return Comment.objects.none()
        return Comment.objects.filter(post_id= post_pk).select_related('owner').annotate(likes_count= Count('liked_by'))
    
    def list(self, request, *args, **kwargs):
        post_pk= self.kwargs.get('post_pk')
        if not Post.objects.filter(pk= post_pk).exists():
            raise NotFound("Post not found")
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        post_pk= self.kwargs.get('post_pk')
        post= get_object_or_404(Post, pk= post_pk)
        serializer.save(owner= self.request.user, post= post)

    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def togglelike(self, request, pk= None, post_pk= None):
        user= request.user
        target= self.get_object()
        if target.liked_by.filter(pk= user.pk).exists():
            target.liked_by.remove(user)
            return Response({'detail': 'unliked', 'likes_count': target.liked_by.count()}, status= status.HTTP_200_OK)
        else:
            target.liked_by.add(user)
            return Response({'detail': 'liked', 'likes_count': target.liked_by.count()}, status= status.HTTP_201_CREATED)


class UserViewSet(ModelViewSet):
    serializer_class= UserSerializer
    permission_classes= [permissions.IsAuthenticated, IsMeOrReadOnly]
    pagination_class= SocialPangination
    http_method_names= ['get', 'put', 'patch', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Creating user is not allowed in this path'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def followers(self, request, pk= None):
        target= self.get_object()
        qs= User.objects.filter(follows__following= target).distinct()
        is_following_subquery= User.objects.filter(followed_by__follower= request.user, pk= OuterRef('pk'))
        qs= qs.annotate(is_following= Exists(is_following_subquery))

        page= self.paginate_queryset(qs)
        if page is not None:
            serializer= self.get_serializer(page, many= True)
            return self.get_paginated_response(serializer.data)
        serializer= self.get_serializer(qs, many= True)
        return Response(serializer.data)

    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def following(self, request, pk= None):
        target= self.get_object()
        qs= User.objects.filter(followed_by__follower= target).distinct()
        is_following_subquery= User.objects.filter(followed_by__follower= request.user, pk= OuterRef('pk'))
        qs= qs.annotate(is_following= Exists(is_following_subquery))

        page= self.paginate_queryset(qs)
        if page is not None:
            serializer= self.get_serializer(page, many= True)
            return self.get_paginated_response(serializer.data)
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
        
    def get_queryset(self):
        user= self.request.user
        is_following_query= Follow.objects.filter(follower= user, following= OuterRef('pk'))

        return User.objects.annotate(
            is_following= Exists(is_following_query)).all()
    

class FollowingPostList(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= SocialPangination

    def get_queryset(self):
        user= self.request.user
        following_ids= Follow.objects.filter(follower= user).values_list('following_id', flat= True)
        qs= Post.objects.select_related('owner').annotate(likes_count= Count('liked_by', distinct= True), comments_count= Count('comments')).filter(owner_id__in= following_ids)
        return qs