from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_nested.routers import NestedSimpleRouter


router= DefaultRouter()
router.register(r'posts', views.PostViewSet, basename= 'posts')
router.register(r'users', views.UserViewSet, basename= 'users')
router.register(r'follow-requests', views.FollowRequestViewSet, basename= 'follow-request')

posts_router= NestedSimpleRouter(router, r'posts', lookup= 'post')
posts_router.register(r'comments', views.CommentViewSet, basename= 'post-comments')


urlpatterns= [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    path('register/', views.RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('following-posts/', views.FollowingPostList.as_view()),
    path('bookmarks/', views.BookmarkAPIView.as_view()),
    path('blocks/', views.BlockListAPI.as_view(), name= 'block-list'),
]