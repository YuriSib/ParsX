from django.db import models
from django.contrib.postgres.fields import ArrayField
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


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
    parent_id = models.IntegerField(unique=False, null=True)
    vk_id = models.IntegerField(unique=True)
    vk_parent_id = models.IntegerField()


class Products(models.Model):
    sbis_id = models.CharField(max_length=20, unique=True, null=False)
    vk_id = models.IntegerField(unique=True, null=True)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, unique=True, null=True)
    description = models.TextField(null=True)
    parameters = models.JSONField(null=True)
    images = ArrayField(
        models.TextField(),
        blank=True,
        default=list,
        null=True
    )
    price = models.IntegerField(null=True)
    old_price = models.IntegerField(null=True, blank=True)
    stocks_mol = models.IntegerField(null=True)
    unisiter_url = models.TextField(null=True)
    customer = models.ForeignKey(Integrations, on_delete=models.SET_NULL, null=True)
