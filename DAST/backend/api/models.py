from django.db import models

# Create your models here.
class Website(models.Model):
    name = models.CharField(unique=True, max_length=100)
    url = models.CharField(unique=True, max_length=100)
    scanned = models.BooleanField(default=False)

    def __str__(self):
        return self.name