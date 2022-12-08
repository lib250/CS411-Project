from django.db import models

# Create your models here.
class SearchHistory(models.Model):
    uid = models.CharField(max_length=100)
    history = models.CharField(max_length=500)
