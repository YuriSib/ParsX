from django.db import models


class Messages(models.Model):
    username = models.CharField(max_length=20, verbose_name='Имя клиента', unique=False)
    authorization = models.BooleanField(verbose_name='Авторизован ли клиент', default=False)
    questions = models.TextField(verbose_name='Вопрос')

    def __str__(self):
        return f'{self.username}: {self.questions}'
