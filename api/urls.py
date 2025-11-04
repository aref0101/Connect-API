from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router= DefaultRouter()
router.register(r'posts', views.PostAPIViewSet, basename= 'posts')
router.register(r'comments', views.CommentViewSet)
router.register(r'users', views.UserViewSet)


urlpatterns= [
    path('register/', views.RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('', include(router.urls)),
    path('following-posts/', views.FollowingPostList.as_view()),
]