from django.db import models

# Create your models here.


class CommandLog(models.Model):

    STATUS_CHOICES = (
        ("pending", "pending"),
        ("skipped", "skipped"),
        ("finished", "finished"),
    )

    name = models.TextField()
    status = models.TextField(choices=STATUS_CHOICES, default="pending")
    create_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "name"])
        ]
