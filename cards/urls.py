from django.urls import path
from . import views

# urlpatterns = [
#     path('catalog/<int:card_id>/', views.get_card_by_id, name='card_detail'),
#     path('catalog/<slug:slug>/', views.get_category_by_name, name='category'),
#     path('catalog/', views.catalog, name='all_cards'),
# ]
urlpatterns = [
    path('catalog/', views.get_all_cards, name='catalog'),  # Общий каталог всех карточек
    path('categories/', views.get_categories, name='categories'),  # Список всех категорий
    path('categories/<slug:slug>/', views.get_cards_by_category, name='category'),  # Карточки по категории
    path('tag/', views.get_detail_card_by_id, name='detail_card_by_id'),
    # Детальная информация по карточкеs/<slug:slug>/', views.get_cards_by_tag, name='tag'),  # Карточки по тегу
    #     path('<int:card_id>/detail
]
