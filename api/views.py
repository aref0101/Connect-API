from rest_framework.viewsets import ModelViewSet
from .models import Post, Comment
from .serializers import PostSerializer, UserRegisterSerializer, CommentSerializer
from rest_framework import generics, permissions, viewsets, status
from .customPermission import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action


class PostAPIViewSet(ModelViewSet):
    queryset= Post.objects.all()
    serializer_class= PostSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ('like', 'unlike'):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()  

    @action(detail= True, methods= ['post'])
    def like(self, request, version= None, pk= None):
        post= self.get_object()
        user= request.user
        post.liked_by.add(user)
        return Response({'status': 'liked', 'likes_count': post.liked_by.count()})

    @action(detail= True, methods= ['post'])
    def unlike(self, request, version= None, pk= None):
        post= self.get_object()
        user= request.user
        post.liked_by.remove(user)
        return Response({'status': 'unliked', 'likes_count': post.liked_by.count()})

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)


class RegisterView(generics.CreateAPIView):
    serializer_class= UserRegisterSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset= Comment.objects.all()
    serializer_class= CommentSerializer
    permission_classes= [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner= self.request.user)