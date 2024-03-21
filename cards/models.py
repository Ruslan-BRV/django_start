from django.db import models

# Create your models here.
class Card(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(max_length=5000)
    upload_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    adds = models.IntegerField(default=0)

    class Meta:
        db_table = 'Cards'
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'

    def __str__(self):
        return f'Карточка {self.question} - {self.answer[:50]}'
    