from django.http import HttpResponse


def appengine_warmup(request):
    return HttpResponse("Successfully Warmed Up.")
