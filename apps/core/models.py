from django.db import models


class Visit(models.Model):
    ip_address = models.CharField(max_length=200, blank=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visited_at"]

    def __str__(self):
        return f"{self.ip_address} - {self.path}"

class SystemSeed(models.Model):
    key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key
