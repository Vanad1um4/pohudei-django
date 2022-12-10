from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    user_id = models.PositiveSmallIntegerField(blank=True)
    weights_to_pull = models.PositiveSmallIntegerField(default=5)  # pyright: ignore

    def __str__(self):
        return str(self.profile)
