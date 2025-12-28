from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.

class CustomUser(AbstractUser):
    name= models.CharField(max_length= 200)
    username= models.CharField(max_length= 200, unique= True)
    bio= models.TextField(blank= True, null= True)
    is_private= models.BooleanField(default= False)
    created_at= models.DateTimeField(auto_now_add= True, db_index= True)

    def __str__(self):
        return self.username
    
    USERNAME_FIELD= 'username'
    REQUIRED_FIELDS= []


class Post(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    text= models.TextField(blank= True, null= True)
    picture= models.ImageField(blank= True, null= True, upload_to= 'posts/')
    bookmarked_by= models.ManyToManyField(settings.AUTH_USER_MODEL, related_name= 'bookmarked_posts', blank= True, db_index= True)
    created_at= models.DateTimeField(auto_now_add= True, db_index= True)

    def clean(self):
        if not self.text and not self.picture:
            raise ValidationError('Post can not be empty')

    def __str__(self):
        return self.text[0:50]
    

class Comment(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'comments')
    post= models.ForeignKey(Post, on_delete= models.CASCADE, related_name= 'comments')
    text= models.TextField()
    created_at= models.DateTimeField(auto_now_add= True, db_index= True)

    def __str__(self):
        return self.text[0:50]
    

class Like(models.Model):
    owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'likes')
    post= models.ForeignKey(Post, on_delete= models.CASCADE, null= True, blank= True, related_name= 'likes')
    comment= models.ForeignKey(Comment, on_delete= models.CASCADE, null= True, blank= True, related_name= 'likes')
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        indexes= [
            models.Index(fields= ['owner', 'post']),
            models.Index(fields= ['owner', 'comment']),
        ]

    def __str__(self):
        if self.post is not None:
            return f'{self.owner} liked the post -> {self.post.text[0:50]}'
        else:
            return f'{self.owner} liked the comment -> {self.comment.text[0:50]}'
    

class Follow(models.Model):
    follower= models.ForeignKey(settings.AUTH_USER_MODEL, related_name= 'follows', on_delete= models.CASCADE)
    following= models.ForeignKey(settings.AUTH_USER_MODEL, related_name= 'followed_by', on_delete= models.CASCADE)
    is_accepted= models.BooleanField(default= True, db_index= True)
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together= ('follower', 'following')
        indexes= [ 
            models.Index(fields= ['follower', 'following']),
        ]

    def __str__(self):
        return f"{self.follower} -> {self.following}"


class Block(models.Model):
    blocker= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'blocks')
    blocking= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'blocked_by')
    created_at= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f'{self.blocker} blocked -> {self.blocking}'