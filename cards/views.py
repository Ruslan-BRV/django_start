from django.http import HttpResponse
from django.shortcuts import render

cards_dataset = [
    {"question": "Что такое PEP 8?",
     "answer": "PEP 8 — стандарт написания кода на Python.",
     "category": "Стандарты кода",
     "tags": ["PEP 8", "стиль", "форматирование"],
     "id_author": 1,
     "id_card": 1,
     "upload_date": "2023-01-15",
     "views_count": 100,
     "favorites_count": 25
     },
    {"question": "Как объявить список в Python?",
     "answer": "С помощью квадратных скобок: lst = []",
     "category": "Основы",
     "tags": ["списки", "основы"],
     "id_author": 2,
     "id_card": 2,
     "upload_date": "2023-01-20",
     "views_count": 150,
     "favorites_count": 30
     },
    {"question": "Что делает метод .append()?",
     "answer": "Добавляет элемент в конец списка.",
     "category": "Списки",
     "tags": ["списки", "методы"],
     "id_author": 2,
     "id_card": 3,
     "upload_date": "2023-02-05",
     "views_count": 75,
     "favorites_count": 20
     },
    {"question": "Какие типы данных в Python иммутабельные?",
     "answer": "Строки, числа, кортежи.",
     "category": "Типы данных",
     "tags": ["типы данных", "иммутабельность"],
     "id_author": 1,
     "id_card": 4,
     "upload_date": "2023-02-10",
     "views_count": 90,
     "favorites_count": 22
     },
    {"question": "Как создать виртуальное окружение в Python?",
     "answer": "С помощью команды: python -m venv myenv",
     "category": "Виртуальные окружения",
     "tags": ["venv", "окружение"],
     "id_author": 2,
     "id_card": 5,
     "upload_date": "2023-03-01",
     "views_count": 120,
     "favorites_count": 40
     }
]

info = {
    "users_count": 100500,
    "cards_count": 200600,
    # "menu": ['Главная', 'О проекте', 'Каталог']
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
    ],
    "cards": cards_dataset  # Добавим в контекст шаблона информацию о карточках, чтобы все было в одном месте
}

# class Info:
#     user_count = 100600
#     cards_count = 200700

# info = Info()
# info = {
#     "info": info,

# }

# def main(request):
#     return HttpResponse("Привет мир!", status=200)
# def get_card_by_id(request, card_id):
#     return HttpResponse(f"Карточка {card_id}")

# def catalog(request):
#     """
#     Принимает информацию о проекте (словарь info)
#     Возвращает шаблон по адресу templates/cards/catalog.html
#     :param request:
#     :return:
#     """
#     return render(request, 'cards/catalog.html', context=info)

# def get_category_by_name(request, slug):
#     return HttpResponse(f"Категория {slug}", status=200)


def main(request):
    """Представление рендерит шаблон base.html"""
    return render(request, 'main.html', context=info)

def about(request):
    """Представление использует шаблон about.html"""
    return render(request, 'about.html', context=info)

def get_all_cards(request):
    """
    Возвращает все карточки для представления в каталоге
    """
    return render(request, 'cards/catalog.html', context=info)


def get_categories(request):
    """
    Возвращает все категории для представления в каталоге
    """
    return HttpResponse('All categories')


def get_cards_by_category(request, slug):
    """
    Возвращает карточки по категории для представления в каталоге
    """
    return HttpResponse(f'Cards by category {slug}')


def get_cards_by_tag(request, slug):
    """
    Возвращает карточки по тегу для представления в каталоге
    """
    return HttpResponse(f'Cards by tag {slug}')


def get_detail_card_by_id(request, card_id):
    """
    Возвращает детальную информацию по карточке для представления
    """
    return HttpResponse(f'Detail card by id {card_id}')
