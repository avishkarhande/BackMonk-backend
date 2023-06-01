from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Models(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=60)
    priority = models.IntegerField()
    json = models.TextField()
    model = models.TextField()
    description = models.TextField(default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
