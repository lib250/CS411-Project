from django.db import models

# Create your models here.

""" 
A search history will be stored in the database
with a uid field corresponding to the user's
Spotify ID and a history field which is a string
containing the user's most recent 5 searches in order
delimited by ';'. 

A ',' separates the name and region within each entry.

For example:
name1,reg1;name2,reg2;name3,reg3

"""
class SearchHistory(models.Model):
    uid = models.CharField(max_length=100)
    history = models.CharField(max_length=500)
