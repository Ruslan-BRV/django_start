from django.contrib import admin
from django.template.defaultfilters import length
from .models import Card

# admin.site.register(Card)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
     # Поля, которые будут отображаться в админке
    list_display = ('id', 'question', 'category', 'views', 'upload_date', 'status', 'brief_info')
    # Поля, которые будут ссылками
    list_display_links = ('id',)
    # Поля по которым будет поиск
    search_fields = ('question', 'answer')
    # Поля по которым будет фильтрация
    list_filter = ('category', 'upload_date', 'status')
    # Ordering - сортировка
    ordering = ('-upload_date',)
    # List_per_page - количество элементов на странице
    list_per_page = 25
    # Поля, которые можно редактировать
    list_editable = ('views', 'question', 'status')
    actions = ['set_checked', 'set_unchecked']

    @admin.action(description="Пометить как проверенное")
    def set_checked(self, request, queryset):
        updated_count = queryset.update(status=Card.Status.CHECKED)
        self.message_user(request, f"{updated_count} записей было помечено как проверенное")

    @admin.action(description="Пометить как не проверенное")
    def set_unchecked(self, request, queryset):
        updated_count = queryset.update(status=Card.Status.UNCHECKED)
        self.message_user(request, f"{updated_count} записей было помечено как непроверенное")

    # Определение метода для отображения краткой информации о карточке
    @admin.display(description="Наличие кода",
                   ordering='answer')  # ordering по полю answer, так как точного поля для сортировки по краткому описанию нет
    def brief_info(self, card):
        # Проверяем наличие кода
        has_code = 'Да' if '```' in card.answer else 'Нет'
        return has_code
    