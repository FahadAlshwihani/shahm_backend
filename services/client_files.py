from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name


class ClientFile(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="clients/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
