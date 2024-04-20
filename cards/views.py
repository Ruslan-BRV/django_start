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
from functools import cached_property
import os
from re import search
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.context_processors import request
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import CreateView
from cards.forms import CardForm, SearchCardsForm, UploadFileForm
from django.views.decorators.cache import cache_page
from django.core.cache import cache
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


class MenuMixin:
    """
    Класс-миксин для добавления меню в контекст шаблона
    Добывает и кеширует cards_count, users_count, menu
    """
    timeout = 30

    def get_menu(self):
        menu = cache.get('menu')
        if not menu:
            menu = info['menu']
            cache.set('menu', menu, timeout=self.timeout)

        return menu
    
    def get_cards_count(self):
        cards_count = cache.get('cards_count')
        if not cards_count:
            cards_count = Card.objects.count()
            cache.set('cards_count', cards_count, timeout=self.timeout)

        return cards_count
    
    def get_users_count(self):
        users_count = cache.get('users_count')
        if not users_count:
            users_count = get_user_model().objects.count()
            cache.set('users_count', users_count, timeout=self.timeout)

        return users_count
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = self.get_menu()
        context['cards_count'] = self.get_cards_count()
        context['users_count'] = self.get_users_count()
        return context


class AboutView(MenuMixin, TemplateView):
    template_name = 'about.html'
    extra_context = {'title': 'О проекте'}




class IndexView(MenuMixin, TemplateView):
    template_name = 'main.html'   

class PageNotFoundView(MenuMixin, TemplateView):
    template_name = '404.html'

def index(request):
    """Функция для отображения главной страницы
    будет возвращать рендер шаблона root/templates/main.html"""
    return render(request, "main.html", info)


def about(request):
    """Функция для отображения страницы "О проекте"
    будет возвращать рендер шаблона /root/templates/about.html"""
    return render(request, 'about.html', info)

def catalog(request):
    """Функция для отображения страницы "Каталог"
    будет возвращать рендер шаблона /templates/cards/catalog.html

    - **`sort`** - ключ для указания типа сортировки с возможными значениями: `date`, `views`, `adds`.
    - **`order`** - опциональный ключ для указания направления сортировки с возможными значениями: `asc`, `desc`. По умолчанию `desc`.

    1. Сортировка по дате добавления в убывающем порядке (по умолчанию): `/cards/catalog/`
    2. Сортировка по количеству просмотров в убывающем порядке: `/cards/catalog/?sort=views`
    3. Сортировка по количеству добавлений в возрастающем порядке: `/cards/catalog/?sort=adds&order=asc`
    4. Сортировка по дате добавления в возрастающем порядке: `/cards/catalog/?sort=date&order=asc`

    """

    # Считываем параметры из GET запроса
    sort = request.GET.get('sort', 'upload_date')  # по умолчанию сортируем по дате загрузки
    order = request.GET.get('order', 'desc')  # по умолчанию используем убывающий порядок
    search_query = request.GET.get('search_query', '')  # поиск по карточкам
    page_number = request.GET.get('page', 1)  # номер страницы

    # Сопоставляем параметр сортировки с полями модели
    valid_sort_fields = {'upload_date', 'views', 'adds'}
    if sort not in valid_sort_fields:
        sort = 'upload_date'

    # Обрабатываем порядок сортировки
    if order == 'asc':
        order_by = sort
    else:
        order_by = f'-{sort}'

    # Если человек ничего не искал
    if not search_query:
        # Получаем карточки из БД в ЖАДНОМ режиме многие ко многим tags
        cards = Card.objects.select_related('category').prefetch_related('tags').order_by(order_by)

    # Если человек что-то искал
    else:
        # Попробуем это сделать без жадной загрузки select_related и prefetch_related
        # cards = Card.objects.filter(question__icontains=search_query).order_by(order_by)
        # Получаем карточки из БД в ЖАДНОМ режиме многие ко многим tags
        # cards = Card.objects.filter(question__icontains=search_query).select_related('category').prefetch_related('tags').order_by(order_by)
        # Q объекты и простая загрузка. Вхождение или в вопрос или в ответ
        # cards = Card.objects.filter(Q(question__icontains=search_query) | Q(answer__icontains=search_query)).order_by(order_by)
        # Q объекты и простая загрузка. Вхождение или в вопрос или в ответ или в теги
        # cards = Card.objects.filter(Q(question__icontains=search_query) | Q(answer__icontains=search_query) | Q(tags__name__icontains=search_query)).order_by(order_by)
        # Это же, с жадной загрузкой
        cards = Card.objects.filter(Q(question__icontains=search_query) | Q(answer__icontains=search_query) | Q(tags__name__icontains=search_query)).select_related('category').prefetch_related('tags').order_by(order_by).distinct()
        
    # Создаем объект пагинатора и передаем ему карточки и количество карточек на странице
    paginator = Paginator(cards, 25)

    # Получаем объект страницы
    page_obj = paginator.get_page(page_number)
    form = SearchCardsForm()

    # Подготавливаем контекст и отображаем шаблон
    context = {
        'cards': cards,
        'cards_count': len(cards),
        'menu': info['menu'],
        'page_obj': page_obj,
        "sort": sort, # Передаем, для того чтобы при переходе по страницам сохранялся порядок сортировки
        "order": order, # Аналогично
        "form": form,
    }

    response = render(request, 'cards/catalog.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # - кэш не используется
    response['Expires'] = '0'  # Перестраховка - устаревание кэша
    return response

class CatalogView(ListView):
    model = Card  # Указываем модель, данные которой мы хотим отобразить
    template_name = 'cards/catalog.html'  # Путь к шаблону, который будет использоваться для отображения страницы
    context_object_name = 'cards'  # Имя переменной контекста, которую будем использовать в шаблоне
    paginate_by = 30  # Количество объектов на странице

    # Метод для модификации начального запроса к БД
    def get_queryset(self):
        # Получение параметров сортировки из GET-запроса
        sort = self.request.GET.get('sort', 'upload_date')
        order = self.request.GET.get('order', 'desc')
        search_query = self.request.GET.get('search_query', '')

        # Определение направления сортировки
        if order == 'asc':
            order_by = sort
        else:
            order_by = f'-{sort}'

        # Фильтрация карточек по поисковому запросу и сортировка
        if search_query:
            queryset = Card.objects.filter(
                Q(question__iregex=search_query) |
                Q(answer__iregex=search_query) |
                Q(tags__name__iregex=search_query)
            ).select_related('category').prefetch_related('tags').distinct().order_by(order_by)
        else:
            queryset = Card.objects.select_related('category').prefetch_related('tags').order_by(order_by)
        return queryset

    # Метод для добавления дополнительного контекста
    def get_context_data(self, **kwargs):
        # Получение существующего контекста из базового класса
        context = super().get_context_data(**kwargs)
        # Добавление дополнительных данных в контекст
        context['sort'] = self.request.GET.get('sort', 'upload_date')
        context['order'] = self.request.GET.get('order', 'desc')
        context['search_query'] = self.request.GET.get('search_query', '')
        # Добавление статических данных в контекст, если это необходимо
        context['menu'] = info['menu'] # Пример добавления статических данных в контекст
        context['form'] = SearchCardsForm()
        return context

# @cache_page(60 * 15)
# def catalog(request):
#     """Функция для отображения страницы "Каталог"
#     будет возвращать рендер шаблона /templates/cards/catalog.html"""

#     # Получаем ВСЕ карточки для каталога
#     # cards = Card.objects.all()
#     # sort = request.GET.get('sort', 'upload_date')
#     # order = request.GET.get('order', 'desc')

#     # valid_sort_fields = {'upload_date', 'views', 'adds'}
#     # if sort not in valid_sort_fields:
#     #     sort = 'upload_date'

#     # if order == 'asc':
#     #     order_by = sort
#     # else:
#     #     order_by = f'-{sort}'

#     # cards = Card.objects.all().order_by(order_by)
#     form = SearchCardsForm()
#     queryset = Card.objects.select_related('category').prefetch_related('tags')
#     search_query = request.GET.get('search_query')
#     sort = request.GET.get('sort', 'upload_date')
#     order = request.GET.get('order', 'desc')
#     page_number = request.GET.get('page', 1)

#     if order == 'asc':
#         order_by = sort
#     else:
#         order_by = f'-{sort}'

#     if search_query:
#             queryset = queryset.filter(
#                 Q(question__icontains=search_query) |
#                 Q(answer__icontains=search_query) |
#                 Q(tags__name__icontains=search_query)
#             ).distinct().order_by(order_by)
#     # else:
#     #     queryset = queryset.order_by(order_by)
        
#     cards = queryset.order_by(order_by)
#     paginator = Paginator(cards, 25)

#     page_obj = paginator.get_page(page_number)
#     # Подготавливаем контекст и отображаем шаблон
#     context = {
#         'cards': cards,
#         'cards_count': cards.count(),
#         'menu': info['menu'],
#         'form': form,
#         'page_obj': page_obj,
#     }

#     return render(request, 'cards/catalog.html', context)

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


class CardDetailView(MenuMixin,DetailView):
    model = Card  # Указываем, что моделью для этого представления является Card
    template_name = 'cards/card_detail.html'  # Указываем путь к шаблону для детального отображения карточки
    context_object_name = 'card'  # Переопределяем имя переменной в контексте шаблона на 'card'

    # Метод для добавления дополнительных данных в контекст шаблона
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)  # Получаем исходный контекст от базового класса
    #     context['menu'] = info['menu']  # Добавляем в контекст информацию о меню
    #     context['title'] = f'Карточка: {context["card"].question}'  # Добавляем заголовок страницы
    #     return context

    # Метод для обновления счетчика просмотров при каждом отображении детальной страницы карточки
    def get_object(self, queryset=None):
        # Получаем объект с учетом переданных в URL параметров (в данном случае, pk или id карточки)
        obj = super().get_object(queryset=queryset)
        # Увеличиваем счетчик просмотров на 1 с помощью F-выражения для избежания гонки условий
        Card.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        return obj
    
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
        'menu': info['menu'],
        'form': SearchCardsForm(),
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

# def add_card(request):
#     if request.method == 'POST':
#         form = CardForm(request.POST)
#         if form.is_valid():
#             # Получаем данные из формы
#             # question = form.cleaned_data['question']
#             # answer = form.cleaned_data['answer']
#             # category = form.cleaned_data.get('category', None)

#             # # Сохраняем карточку в БД
#             # card = Card(question=question, answer=answer, category=category)
#             # card.save()
#             # # Получаем id созданной карточки
#             # card_id = card.id

#             # # Перенаправляем на страницу с детальной информацией о карточке
#             # return HttpResponseRedirect(f'/cards/{card_id}/detail/')
#             card = form.save()
#             # Редирект на страницу созданной карточки после успешного сохранения
#             return redirect(card.get_absolute_url())
        
#     else:
#         form = CardForm()

#     return render(request, 'cards/add_card.html', {'form': form, 'menu': info['menu']})


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

class AddCardView(MenuMixin, CreateView):
    model = Card  # Указываем модель, с которой работает представление
    form_class = CardForm  # Указываем класс формы для создания карточки
    template_name = 'cards/add_card.html'  # Указываем шаблон, который будет использоваться для отображения формы
    success_url = reverse_lazy('catalog')  # URL для перенаправления после успешного создания карточки


# class AddCardView(View):
#     def get(self, request):
#         form = CardForm()  # Создаем пустую форму
#         context = {
#             'form': form,
#             # предполагаем, что info['menu'] - это данные, необходимые для отображения меню на странице
#             'menu': info['menu'],  
#         }
#         return render(request, 'cards/add_card.html', context)
    
#     # Метод для обработки POST-запросов
#     def post(self, request):
#         form = CardForm(request.POST)
#         if form.is_valid():
#             card = form.save()  # Сохраняем форму, если она валидна
#             # Перенаправляем пользователя на страницу созданной карточки
#             return redirect(card.get_absolute_url())
#         else:
#             # Если форма не валидна, возвращаем ее обратно в шаблон с ошибками
#             context = {
#                 'form': form,
#                 'menu': info['menu'],
#             }
#             return render(request, 'cards/add_card.html', context)
    
class CardUpdateView(MenuMixin, UpdateView):
    model = Card  # Указываем, что работаем с моделью Card
    form_class = CardForm  # Указываем, что используем форму CardModelForm для редактирования
    template_name = 'cards/add_card.html'  # Указываем шаблон, в котором будет форма редактирования
    # После успешного обновления карточки, пользователь будет перенаправлен на страницу этой карточки
    context_object_name = 'card'
    success_url = reverse_lazy('catalog')  # URL для перенаправления после успешного обновления карточки
    
class CardDeleteView(MenuMixin, DeleteView):
    model = Card  # Указываем, что работаем с моделью Card4
    success_url =  reverse_lazy('catalog')
    template_name = 'cards/delete_card.html'  # Указываем шаблон, в котором будет форма редактирования

