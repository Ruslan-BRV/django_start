from django.http import HttpResponse

def main(request):
    return HttpResponse("Привет мир!", status=200)