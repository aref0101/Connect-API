from rest_framework.viewsets import ModelViewSet
from .models import Post, Comment, Follow, Like, Block
from .serializers import (PostSerializer, CommentSerializer, UserRegisterSerializer, 
    UserSerializer, FollowSerializer, BlockSerializer)
from rest_framework import generics, permissions, viewsets, status
from .customPermission import IsOwnerOrReadOnly, IsMeOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
User= get_user_model()
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Exists, OuterRef, Q
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
        target= self.get_object()
        user= request.user
        if Like.objects.filter(owner= user, post= target).exists():
            Like.objects.filter(owner= user, post= target).delete()
            return Response({'detail': 'unliked', 'likes_count': Like.objects.filter(post= target).count()},
                status= status.HTTP_200_OK)
        else:
            Like.objects.create(owner= user, post= target)
            return Response({'detail': 'liked', 'likes_count': Like.objects.filter(post= target).count()}, 
                status= status.HTTP_201_CREATED)

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

        following_ids= Follow.objects.filter(follower= user, is_accepted= True).values_list('following_id', flat= True)
        blocking_ids= Block.objects.filter(blocker= OuterRef('owner'), blocking= user).values_list('blocker_id', flat= True)
        return Post.objects.filter(
            Q(owner__is_private= False) |
            Q(owner_id__in= following_ids) | 
            Q(owner= user)).filter(
                ~Q(owner_id__in= blocking_ids)
            ).select_related(
                'owner').annotate(
                is_following= Exists(is_following_query),
                likes_count= Count('likes', distinct= True),
                comments_count= Count('comments', distinct= True))
    

class BookmarkAPIView(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= SocialPangination

    def get_queryset(self):
        return Post.objects.select_related('owner').annotate(
            likes_count= Count('likes', distinct= True),
            comments_count= Count('comments', distinct= True)
            ).filter(bookmarked_by= self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class= UserRegisterSerializer


class CommentViewSet(ModelViewSet):
    serializer_class= CommentSerializer
    permission_classes= [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class= SocialPangination

    def get_queryset(self):
        user= self.request.user
        post_pk= self.kwargs.get('post_pk')
        if post_pk is None:
            return Comment.objects.none()
        try:
            post= Post.objects.select_related('owner').get(pk= post_pk) 
        except Post.DoesNotExist:
            return Comment.objects.none()
        
        is_blocked= Block.objects.filter(blocking= user, blocker= post.owner).exists()
        if is_blocked:
            return Comment.objects.none() 

        if post.owner.is_private and post.owner!= user:
            is_following= Follow.objects.filter(follower= user, following= post.owner, is_accepted= True).exists()
            if not is_following:
                raise NotFound('Comment not found')
        return Comment.objects.filter(post= post).select_related('owner').annotate(likes_count= Count('likes'))

    def perform_create(self, serializer):
        user= self.request.user
        post_pk= self.kwargs.get('post_pk')
        post= get_object_or_404(Post, pk= post_pk)

        is_owner= post.owner== user
        is_private= not post.owner.is_private
        is_following= Follow.objects.filter(follower= user, following= post.owner, is_accepted= True).exists()

        if is_owner or is_private or is_following:
            serializer.save(owner= user, post= post)
        else:
            raise NotFound('Comment not found')

    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def togglelike(self, request, pk= None, post_pk= None):
        user= request.user
        target= self.get_object()
        if Like.objects.filter(owner= user, comment= target).exists():
            Like.objects.filter(owner= user, comment= target).delete()
            return Response({'detail': 'unliked', 'likes_count': Like.objects.filter(comment= target).count()}, 
                status= status.HTTP_200_OK)
        else:
            Like.objects.create(owner= user, comment= target)
            return Response({'detail': 'liked', 'likes_count': Like.objects.filter(comment= target).count()}, 
                status= status.HTTP_201_CREATED)


class UserViewSet(ModelViewSet):
    serializer_class= UserSerializer
    permission_classes= [IsAuthenticated, IsMeOrReadOnly]
    pagination_class= SocialPangination
    http_method_names= ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        user= self.request.user
        is_following_query= Follow.objects.filter(follower= user, following= OuterRef('pk'))
        is_blocked= Block.objects.filter(blocker= OuterRef('pk'), blocking= user)
        
        qs= User.objects.annotate(is_following= Exists(is_following_query), is_blocked= Exists(is_blocked))
        qs= qs.exclude(is_blocked= True)
        return qs

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Creating user is not allowed in this path'}, status= status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def followers(self, request, pk= None):
        user= self.request.user
        target= self.get_object()
        following_ids= Follow.objects.filter(follower= user, is_accepted= True).values_list('following_id', flat= True)
        is_following_subquery= User.objects.filter(followed_by__follower= request.user, pk= OuterRef('pk'))

        if (target.is_private== False) or (target== user) or (target.id in following_ids):
            qs= User.objects.filter(follows__following= target, follows__is_accepted= True).annotate(
                is_following= Exists(is_following_subquery)).distinct()

            page= self.paginate_queryset(qs)
            if page is not None:
                serializer= self.get_serializer(page, many= True)
                return self.get_paginated_response(serializer.data)
            serializer= self.get_serializer(qs, many= True)
            return Response(serializer.data)
        else:
            return Response({'detail': 'you dont have permission'}, status= status.HTTP_403_FORBIDDEN)

    @action(detail= True, methods= ['get'], permission_classes= [IsAuthenticated])
    def following(self, request, pk= None):
        user= self.request.user
        target= self.get_object()
        following_ids= Follow.objects.filter(follower= user, is_accepted= True).values_list('following_id', flat= True)
        is_following_subquery= User.objects.filter(followed_by__follower= request.user, pk= OuterRef('pk'))

        if (target.is_private== False) or (target== user) or (target.id in following_ids):
            qs= User.objects.filter(followed_by__follower= target, followed_by__is_accepted= True).annotate(
                is_following= Exists(is_following_subquery)).distinct()

            page= self.paginate_queryset(qs)
            if page is not None:
                serializer= self.get_serializer(page, many= True)
                return self.get_paginated_response(serializer.data)
            serializer= self.get_serializer(qs, many= True)
            return Response(serializer.data)
        else:
            return Response({'detail': 'you dont have permission'}, status= status.HTTP_403_FORBIDDEN)

    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def togglefollow(self, request, pk= None):
        user= request.user
        target= self.get_object()

        if user== target:
            return Response({'detail': 'you cannot follow yourself'}, status= status.HTTP_400_BAD_REQUEST)
        
        follow_instance= Follow.objects.filter(follower= user, following= target).first()
        if follow_instance:
            if follow_instance.is_accepted== True:
                message= 'Unfollowed'
            else:
                message= 'Follow request cancelled.'
            follow_instance.delete()
            return Response({'detail': message})
        else:
            if target.is_private== True:
                Follow.objects.create(follower= user, following= target, is_accepted= False)
                return Response({'detail': 'Follow request sent.'}, status= status.HTTP_201_CREATED)
            else:
                Follow.objects.create(follower= user, following= target, is_accepted= True)
                return Response({'detail': 'followed'}, status= status.HTTP_201_CREATED)
            
    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def toggleblock(self, request, pk= None):
        user= request.user
        target= self.get_object()

        if user== target:
            return Response({'detail': 'you can not block yourself'}, status= status.HTTP_400_BAD_REQUEST)
        elif Block.objects.filter(blocker= user, blocking= target).exists():
            Block.objects.filter(blocker= user, blocking= target).delete()
            return Response({'detail': 'unblocked'}, status= status.HTTP_200_OK)
        else:
            Block.objects.create(blocker= user, blocking= target)
            return Response({'detail': 'blocked'}, status= status.HTTP_201_CREATED)
    

class FollowRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class= FollowSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        user= self.request.user
        return Follow.objects.filter(following= user).select_related('follower', 'following')

    @action(detail= True, methods= ['post'])
    def accept(self, request, pk= None):
        follow_req= get_object_or_404(Follow, pk= pk, is_accepted= False)

        follow_req.is_accepted= True
        follow_req.save()
        return Response({'detail': 'follow request accepted'})
    
    @action(detail= True, methods= ['delete'])
    def decline(self, request, pk= None):
        follow_req= get_object_or_404(Follow, pk= pk, is_accepted= False)

        follow_req.delete()
        return Response({'detail': 'follow request declined'})
    

class FollowingPostList(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= SocialPangination

    def get_queryset(self):
        user= self.request.user
        following_ids= Follow.objects.filter(follower= user, is_accepted= True).values_list('following_id', flat= True)
        return Post.objects.filter(owner_id__in= following_ids).select_related('owner').annotate(
            likes_count= Count('likes', distinct= True), comments_count= Count('comments', distinct= True))
    

class BlockListAPI(generics.ListAPIView):
    serializer_class= BlockSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= SocialPangination

    def get_queryset(self):
        return Block.objects.filter(blocker= self.request.user)