from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    tg_user_id = models.CharField(max_length=255)

    def __str__(self):
        return str(self.profile)
