from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.

class CustomUser(AbstractUser):
    name= models.CharField(max_length= 200)
    username= models.CharField(max_length= 200, unique= True)
    bio= models.TextField(blank= True, null= True)

    def __str__(self):
        return self.username
    
    USERNAME_FIELD= 'username'
    REQUIRED_FIELDS= []


class Post(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    text= models.TextField(blank= True, null= True)
    picture= models.ImageField(blank= True, null= True, upload_to= 'posts/')
    liked_by= models.ManyToManyField(settings.AUTH_USER_MODEL, related_name= 'liked_posts', blank= True)
    created= models.DateTimeField(auto_now_add= True)

    def clean(self):
        if not self.text and not self.picture:
            raise ValidationError('Post can not be empty')

    def __str__(self):
        return self.text[0:50]
    

class Comment(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    post= models.ForeignKey(Post, on_delete= models.CASCADE)
    text= models.TextField()
    created= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.text[0:50]