from django.db import models
from django.contrib.postgres.fields import ArrayField


class Integrations(models.Model):
    name = models.CharField(max_length=255, unique=False, null=True)
    authorization_code = models.CharField(max_length=400, unique=False, null=True)

    code_challenge = models.CharField(max_length=130, unique=False, null=True)
    code_verifier = models.CharField(max_length=130, unique=False, null=True)
    state = models.CharField(max_length=130, unique=False, null=True)
    device_id = models.CharField(max_length=255, unique=False, null=True)

    refresh_token = models.CharField(max_length=400, unique=False, null=True)
    access_token = models.CharField(max_length=400, unique=False, null=True)


class Categories(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True)
    parent_id = models.IntegerField()
    vk_id = models.IntegerField(unique=True)
    vk_parent_id = models.IntegerField()


class Products(models.Model):
    sbis_id = models.CharField(max_length=20, unique=True, null=False)
    vk_id = models.IntegerField(unique=True)
    category_id = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField()
    parameters = models.JSONField()
    images = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    price = models.IntegerField()
    stocks_mol = models.IntegerField()
    unisiter_url = models.TextField()

