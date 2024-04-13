from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from .models import Card, Category, Tag
# from .validators import CodeBlockValidator  # Предполагается, что класс валидатора определен в validators.py

class CardForm(forms.ModelForm):
    # Определяем поля формы, связываем с моделью Card и добавляем дополнительные настройки
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Категория не выбрана", label='Категория', widget= forms.Select(attrs={'class': 'form-control'}))
    tags = forms.CharField(label='Теги', required=False, help_text='Перечислите теги через запятую', widget= forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Card
        fields = ['question', 'answer', 'category', 'tags']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 40}),
        }
        labels = {
            'question': 'Вопрос',
            'answer': 'Ответ',
            'category': 'Категория',
            'tags': 'Теги',
        }
    
    def clean_tags(self):
        # Валидация и преобразование строки тегов в список тегов
        tags_str = self.cleaned_data['tags']
        tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return tag_list
    
    def save(self, *args, **kwargs):
        # Сохранение карточки вместе с тегами
        instance = super().save(commit=False)
        instance.save()  # Сначала сохраняем карточку, чтобы получить ее id

        # Обрабатываем теги
        for tag_name in self.cleaned_data['tags']:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)
        
        return instance
    

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Выберите файл', widget=forms.FileInput(attrs={'class': 'form-control'}))

class SearchCardsForm(forms.Form):
    search_query = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))