from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router= DefaultRouter()
router.register(r'posts', views.PostAPIViewSet)
router.register(r'comments', views.CommentViewSet)


urlpatterns= [
    path('register/', views.RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('', include(router.urls)),
]