from django.http import HttpResponse

def main(request):
    return HttpResponse("Привет мир!", status=200)
def get_card_by_id(request, card_id):
    return HttpResponse(f"Карточка {card_id}")

def catalog(request):
    return HttpResponse("Каталог карточек")

def get_category_by_name(request, slug):
    return HttpResponse(f"Категория {slug}")
