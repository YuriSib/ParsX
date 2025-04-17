from django.db import models
from tinymce import models as tinymce_models


class Articles(models.Model):
    """Непосредственно услуги"""
    name = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, unique=True)
    description = tinymce_models.HTMLField()

    def __str__(self):
        return self.name
