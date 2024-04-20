# /cards/urls.py
from django.urls import path
from . import views

# Префикс /cards/
urlpatterns = [
    path('catalog/', views.CatalogView.as_view(), name='catalog'),  # Общий каталог всех карточек
    path('categories/', views.get_categories, name='categories'),  # Список всех категорий
    path('categories/<slug:slug>/', views.get_cards_by_category, name='category'),  # Карточки по категории
    # path('tags/<slug:slug>/', views.get_cards_by_tag, name='tag'),  # Карточки по тегу
    path('<int:pk>/detail/', views.CardDetailView.as_view(), name='detail_card_by_id'),
    path('<int:pk>/edit/', views.CardUpdateView.as_view(), name='edit_card'),
    path('<int:pk>/delete/', views.CardDeleteView.as_view(), name='delete_card'),
    path('tags/<int:tag_id>/', views.get_cards_by_tag, name='cards_by_tag'),
    path('preview_card_ajax/', views.preview_card_ajax, name='preview_card_ajax'),
    # path('add/', views.add_card, name='add_card'),
    path('add_file/', views.add_card_by_file, name='add_card_by_file'),
    path('add/', views.AddCardView.as_view(), name='add_card'),
]
