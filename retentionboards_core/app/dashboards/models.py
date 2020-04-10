from django.db import models
from users.models import User
from enum import Enum


class EventsetStatus(Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    FAILED = "Failed"
    PROGRESS = "Progress"
    NEW = "New"


class EventSet(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=120,
        choices=[(tag, tag.value) for tag in EventsetStatus]
    )
    step_matrix_task_id = models.CharField(max_length=120)
    tsne_task_id = models.CharField(max_length=120)
    events = models.IntegerField(null=True)
    users = models.IntegerField(null=True)
    unique_events = models.IntegerField(null=True)

    @property
    def processing(self):
        return self.status != EventsetStatus.SUCCESS

    @property
    def events_per_user(self):
        return "{0:.2f}".format(self.events/self.users)


    @property
    def href(self):
        return "/web/app/dashboard/experiments/" + str(self.id)

    @classmethod
    def get_eventset_list(cls, user):
        eventsets = EventSet.objects.filter(user=user)
        eventsets_list = []
        first = 0
        counter = 0
        row = 0
        eventsets_list.append([])
        for eventset in eventsets:
            if first < 2:
                eventsets_list[0].append(eventset)
                first += 1
            if first == 2:
                counter = 3
                first += 1
                continue
            if first > 2:
                if counter == 3:
                    eventsets_list.append([])
                    row += 1
                    counter = 0
                eventsets_list[row].append(eventset)
                counter += 1
        return eventsets_list


class Event(models.Model):
    event_name = models.CharField(max_length=150)
    event_timestamp = models.CharField(max_length=150)
    user_pseudo_id = models.CharField(max_length=150)
    event_set = models.ForeignKey(EventSet, on_delete=models.CASCADE)
