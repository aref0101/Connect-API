from rest_framework.viewsets import ModelViewSet
from .models import Post, Comment, Follow
from .serializers import PostSerializer, UserRegisterSerializer, CommentSerializer, UserSerializer
from rest_framework import generics, permissions, viewsets, status
from .customPermission import IsOwnerOrReadOnly, IsMeOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
User= get_user_model()
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count


class PostAPIViewSet(ModelViewSet):
    serializer_class= PostSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly] 

    @action(detail= True, methods= ['post'], permission_classes= [permissions.IsAuthenticated])
    def like(self, request, pk= None):
        post= self.get_object()
        user= request.user
        post.liked_by.add(user)
        return Response({'detail': 'liked', 'likes_count': post.liked_by.count()})

    @action(detail= True, methods= ['post'], permission_classes= [permissions.IsAuthenticated])
    def unlike(self, request, pk= None):
        post= self.get_object()
        user= request.user
        post.liked_by.remove(user)
        return Response({'detail': 'unliked', 'likes_count': post.liked_by.count()})

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)

    def get_queryset(self):
        return Post.objects.all().annotate(comments_count= Count('comments')).order_by('-created')


class RegisterView(generics.CreateAPIView):
    serializer_class= UserRegisterSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset= Comment.objects.all().order_by('-created')
    serializer_class= CommentSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    @action(detail= True, methods= ['post'], permission_classes= [permissions.IsAuthenticated])
    def like(self, request, pk= None):
        comment= self.get_object()
        user= request.user
        comment.liked_by.add(user)
        return Response({'detail': 'liked', 'likes_count': comment.liked_by.count()})
    
    @action(detail= True, methods= ['post'], permission_classes= [permissions.IsAuthenticated])
    def unlike(self, request, pk= None):
        comment= self.get_object()
        user= request.user
        comment.liked_by.remove(user)
        return Response({'detail': 'unliked', 'likes_count': comment.liked_by.count()})

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
    def follow(self, request, pk= None):
        target= self.get_object()
        user= request.user
        if user== target:
            return Response({'detail': 'you cannot follow yourself'}, status= status.HTTP_400_BAD_REQUEST)
        followed_obj, created= Follow.objects.get_or_create(follower= user, following= target)
        if created:
            return Response({'detail': 'followed'}, status= status.HTTP_201_CREATED)
        return Response({'detail': 'already following'}, status= status.HTTP_200_OK)
    
    @action(detail= True, methods= ['post'], permission_classes= [IsAuthenticated])
    def unfollow(self, request, pk= None):
        target= self.get_object()
        user= request.user
        deleted, _ = Follow.objects.filter(follower= user, following= target).delete()
        if deleted:
            return Response({'detail': 'unfollowed'}, status= status.HTTP_200_OK)
        return Response({'detail': 'not following'}, status= status.HTTP_400_BAD_REQUEST)
    

class FollowingPostList(generics.ListAPIView):
    serializer_class= PostSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        user= self.request.user
        following_ids= Follow.objects.filter(follower= user).values_list('following_id', flat= True)
        qs= Post.objects.filter(owner_id__in= following_ids).order_by('-created')
        return qs