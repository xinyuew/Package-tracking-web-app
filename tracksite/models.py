from django.contrib.auth.models import User
from django.db import models


class TrackInfo(models.Model):
    trackNum = models.CharField(max_length=250, default="")
    details = models.CharField(max_length=65535, default="")
    carrier = models.CharField(max_length=250, default="")
    last_update = models.DateTimeField()
    est_delivery_date = models.DateTimeField(blank=True, null=True)


class Profile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=50, blank=True)
    age = models.CharField(max_length=50, default="", blank=True)
    location = models.CharField(max_length=200, default="", blank=True)
    bio = models.CharField(max_length=420, default="", blank=True)
    picture = models.ImageField(upload_to="tracksite-photos", blank=True, default="tracksite-photos/default.jpg")
    tracks = models.ManyToManyField(TrackInfo)
    roommates = models.ManyToManyField(User, related_name='roommates')

    def __unicode__(self):
        return self.first_name + " " + self.last_name
