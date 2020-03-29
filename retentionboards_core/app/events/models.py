from django.db import models
from users.models import User


# Create your models here.
class EventSet(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Event(models.Model):
    event_name = models.CharField(max_length=150)
    event_timestamp = models.CharField(max_length=150)
    user_pseudo_id = models.CharField(max_length=150)
    event_set = models.ForeignKey(EventSet, on_delete=models.CASCADE)
