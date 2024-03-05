from django.http import HttpResponse

def main(request):
    return HttpResponse("Привет мир!", status=200)

def card_by_id(request, card_id):
    if card_id > 10:
        return HttpResponse("Карточки нет!", status=404)
    return HttpResponse(f"Вы открыли карточку {card_id}")

def get_all_cards(request):
    return HttpResponse("Все карточки")