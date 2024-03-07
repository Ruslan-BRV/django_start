from django.http import HttpResponse
from django.shortcuts import render

info = {
    "users_count": 100600,
    "cards_count": 100600,
    "menu": [
        {"title": "Главная",
         "url": "/",
         "url_name": "index"},
        {"title": "О проекте",
         "url": "/about/",
         "url_name": "about"},
        {"title": "Каталог",
         "url": "/cards/catalog/",
         "url_name": "catalog"},
    ]
}

# class Info:
#     user_count = 100600
#     cards_count = 200700

# info = Info()
# info = {
#     "info": info,

# }

def main(request):
    return HttpResponse("Привет мир!", status=200)
def get_card_by_id(request, card_id):
    return HttpResponse(f"Карточка {card_id}")

def catalog(request):
    """
    Принимает информацию о проекте (словарь info)
    Возвращает шаблон по адресу templates/cards/catalog.html
    :param request:
    :return:
    """
    return render(request, 'cards/catalog.html', context=info)

def get_category_by_name(request, slug):
    return HttpResponse(f"Категория {slug}")
