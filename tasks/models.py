from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    provider_id = models.IntegerField(null=True, blank=True)  # TMDB TV id
    platform = models.CharField(max_length=30, default="MANUAL", blank=True)  # NETFLIX/PRIME/APPLE/MANUAL
    rating = models.FloatField(null=True, blank=True)
    poster_url = models.URLField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "platform", "provider_id"], name="uniq_user_platform_provider")
        ]

    def __str__(self):
        return self.title
