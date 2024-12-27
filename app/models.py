from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    total_points = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False) 
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  
        blank=True
    )

    def __str__(self):
        return self.username

    def __str__(self):
        return self.username


class AndroidApp(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=100, default='default_value') 
    sub_category = models.CharField(max_length=100,default='default_value')  
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserTask(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    app = models.ForeignKey(AndroidApp, on_delete=models.CASCADE, related_name='user_tasks')
    screenshot = models.ImageField(upload_to='task_screenshots/')
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.app.name}"

