from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Team(models.Model):
    name = models.CharField(max_length=255)

class Membership(models.Model):
    ROLE_CHOICES = (
        ('Manager', 'Manager'),
        ('Viewer', 'Viewer')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

