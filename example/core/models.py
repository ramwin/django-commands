from django.db import models

# Create your models here.


class Node(models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    note = models.TextField(default="")


class Leaf(models.Model):
    parent = models.ForeignKey(Node, on_delete=models.CASCADE)
