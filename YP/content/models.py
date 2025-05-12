from django.db import models
from tinymce.models import HTMLField
from django.utils.text import slugify


class Articles(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, unique=True)
    content = HTMLField(default='Тут будет html статьи')

    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
