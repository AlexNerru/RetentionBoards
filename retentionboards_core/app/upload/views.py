from django.http import HttpResponse

from .tasks import publish_message

def my_pub_view(request):
    publish_message({'hello': 'world'})
    return HttpResponse(status=201)