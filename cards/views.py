"""
cards/views.py
index - возвращает главную страницу - шаблон /templates/cards/main.html
about - возвращает страницу "О проекте" - шаблон /templates/cards/about.html
catalog - возвращает страницу "Каталог" - шаблон /templates/cards/catalog.html


get_categories - возвращает все категории для представления в каталоге
get_cards_by_category - возвращает карточки по категории для представления в каталоге
get_cards_by_tag - возвращает карточки по тегу для представления в каталоге
get_detail_card_by_id - возвращает детальную информацию по карточке для представления

render(запрос, шаблон, контекст=None)
    Возвращает объект HttpResponse с отрендеренным шаблоном шаблон и контекстом контекст.
    Если контекст не передан, используется пустой словарь.
"""

# from unicodedata import category
import os
from re import search
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.context_processors import request
from django.template.loader import render_to_string
from cards.forms import CardForm, SearchCardsForm, UploadFileForm
from django.views.decorators.cache import cache_page

# import cards
from cards.models import Card
from cards.templatetags.markdown_to_html import markdown_to_html

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
         {"title": "Добавить карточку",
         "url": "/cards/add/",
         "url_name": "add_card"},
    ]
}


def index(request):
    """Функция для отображения главной страницы
    будет возвращать рендер шаблона root/templates/main.html"""
    return render(request, "main.html", info)


def about(request):
    """Функция для отображения страницы "О проекте"
    будет возвращать рендер шаблона /root/templates/about.html"""
    return render(request, 'about.html', info)

@cache_page(60 * 15)
def catalog(request):
    """Функция для отображения страницы "Каталог"
    будет возвращать рендер шаблона /templates/cards/catalog.html"""

    # Получаем ВСЕ карточки для каталога
    # cards = Card.objects.all()
    sort = request.GET.get('sort', 'upload_date')
    order = request.GET.get('order', 'desc')

    valid_sort_fields = {'upload_date', 'views', 'adds'}
    if sort not in valid_sort_fields:
        sort = 'upload_date'

    if order == 'asc':
        order_by = sort
    else:
        order_by = f'-{sort}'

    # cards = Card.objects.all().order_by(order_by)
    form = SearchCardsForm()
    queryset = Card.objects.select_related('category').prefetch_related('tags')
    search_query = request.GET.get('search_query')
    if search_query:
            queryset = queryset.filter(
                Q(question__icontains=search_query) |
                Q(answer__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct().order_by(order_by)
    # else:
    #     queryset = queryset.order_by(order_by)
    cards = queryset.order_by(order_by)
    # Подготавливаем контекст и отображаем шаблон
    context = {
        'cards': cards,
        'cards_count': cards.count(),
        'menu': info['menu'],
        'form': form,
    }

    return render(request, 'cards/catalog.html', context)

def get_categories(request):
    """
    Возвращает все категории для представления в каталоге
    """
    # Проверка работы базового шаблона
    return render(request, 'base.html', info)


def get_cards_by_category(request, slug):
    """
    Возвращает карточки по категории для представления в каталоге
    """
    return HttpResponse(f'Cards by category {slug}')


# def get_cards_by_tag(request, slug):
#     """
#     Возвращает карточки по тегу для представления в каталоге
#     """
#     return HttpResponse(f'Cards by tag {slug}')

def get_detail_card_by_id(request, card_id):

    card = get_object_or_404(Card, pk=card_id)

    card.views = F('views') + 1
    card.save()
    
    card.refresh_from_db()
    context = {
        'card': card,
        'menu': info['menu'],
    }

    return render(request, 'cards/card_detail.html', context)    


def get_cards_by_tag(request, tag_id):
    """
    Возвращает карточки по тегу для представления в каталоге
    """
    cards = Card.objects.filter(tags__id=tag_id)
    context = {
        'cards': cards,
        'cards_count': cards.count(),
        'menu': info['menu']
    }

    return render(request, 'cards/catalog.html', context)


def preview_card_ajax(request):
    if request.method == "POST":
        question = request.POST.get('question', '')
        answer = request.POST.get('answer', '')
        category = request.POST.get('category', '')
        
        # Генерация HTML для предварительного просмотра
        html_content = render_to_string('cards/card_detail.html', {
            'card': {
                'question': question,
                'answer': answer,
                'category': category,
                'tags': ['тест', 'тег']
            }
        })
        
        return JsonResponse({'html': html_content})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def add_card(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            # question = form.cleaned_data['question']
            # answer = form.cleaned_data['answer']
            # category = form.cleaned_data.get('category', None)

            # # Сохраняем карточку в БД
            # card = Card(question=question, answer=answer, category=category)
            # card.save()
            # # Получаем id созданной карточки
            # card_id = card.id

            # # Перенаправляем на страницу с детальной информацией о карточке
            # return HttpResponseRedirect(f'/cards/{card_id}/detail/')
            card = form.save()
            # Редирект на страницу созданной карточки после успешного сохранения
            return redirect(card.get_absolute_url())
        
    else:
        form = CardForm()

    return render(request, 'cards/add_card.html', {'form': form, 'menu': info['menu']})


def handle_uploaded_file(f):
    # Создаем путь к файлу в директории uploads, имя файла берем из объекта f
    file_path = f'uploads/{f.name}'

    # Создаем папку uploads, если ее нет
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    
    # Открываем файл для записи в бинарном режиме (wb+)
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path

def add_card_by_file(request):
    if request.method == 'POST':
        
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Записываем файл на диск
            file_path = handle_uploaded_file(request.FILES['file'])
            
            # Редирект на страницу каталога после успешного сохранения
            return redirect('catalog')
    else:
        form = UploadFileForm()
    return render(request, 'cards/add_file_card.html', {'form': form})