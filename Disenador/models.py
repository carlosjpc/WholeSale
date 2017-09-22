from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
class Designer_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="yo_designer")
    bio = models.TextField(blank=True, null=True)
    created_in = models.IntegerField(blank=True, null=True)
    style = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Designer_Employee(models.Model):
    ASSISTANT = 'JR'
    role_choices = (
        (ASSISTANT, 'Assistant'),
    )
    role = models.CharField(max_length=2, choices=role_choices, default=ASSISTANT)
    works_for = models.ForeignKey(User, blank=True, related_name="boss")
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="yo_d_employee")

    def __str__(self):
        return self.user.username

class BaseItem(models.Model):
    clave = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=140, blank=True, null=True)
    BasePrice = models.DecimalField(max_digits=5, decimal_places=2)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('clave', 'name', 'designer',)

    def get_absolute_url(self):
        return '/designer/base_item_detail/%d/' % self.pk

    def __str__(self):
        return self.name

class Color(models.Model):
    color_or_print = models.CharField(max_length=60)
    color_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to=None, max_length=100, blank=True, null=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    class Meta:
        unique_together = ('color_or_print', 'designer',)

    def get_absolute_url(self):
        return '/designer/color_detail/%d/' % self.pk

    def __str__(self):
        return self.color_or_print

class Material(models.Model):
    name = models.CharField(max_length=60)
    materialPrice = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    class Meta:
        unique_together = ('name', 'designer',)

    def get_absolute_url(self):
        return '/designer/material_detail/%d/' % self.pk

    def __str__(self):
        return self.name

class Size_Group(models.Model):
    group_name = models.CharField(max_length=10)
    default = models.BooleanField(blank=True, default=False)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group_name', 'designer',)

    def get_absolute_url(self):
        return '/designer/siz_group_detail/%d/' % self.pk

    def __str__(self):
        return self.group_name

class Size(models.Model):
    size = models.CharField(max_length=10)
    order = models.PositiveIntegerField(blank=True)
    sizePrice = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    group = models.ForeignKey(Size_Group, on_delete=models.CASCADE, blank=True)
    designer = models.ForeignKey(User)

    def __str__(self):
        return self.size

class Extra_Attribute(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=60)
    attrPrice = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to=None, max_length=100, blank=True, null=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

class Item(models.Model):
    clave = models.CharField(max_length=80)
    base = models.ForeignKey(BaseItem, on_delete=models.CASCADE)
    color_or_print = models.ForeignKey(Color, blank=True, null=True)
    material = models.ForeignKey(Material, blank=True, null=True)
    attribute = models.ForeignKey(Extra_Attribute, blank=True, null=True)
    size_group = models.ForeignKey(Size_Group, blank=True, null=True)
    ItemPrice = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to=None, max_length=100, blank=True, null=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('base', 'color_or_print', 'material', 'attribute', 'size_group'), ('designer', 'clave'))

    def get_absolute_url(self):
        return '/designer/item_detail/%d/' % self.pk

    def __str__(self):
        return self.clave

class Item_Available_Sizes(models.Model):
    SKU = models.CharField(max_length=80)
    item = models.ForeignKey(Item)
    size = models.ForeignKey(Size)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    qty_sold = models.IntegerField(blank=True, null=True)
    qty_shipped = models.IntegerField(blank=True, null=True)
    qty_canceled = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('item', 'size',)

    def __str__(self):
        return self.SKU

class Collection(models.Model):
    season = models.CharField(max_length=10)
    year = models.IntegerField()
    name = models.CharField(max_length=60, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lookbook = models.FileField(upload_to='documents/', blank=True, null=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.season

class Delivery(models.Model):
    number = models.IntegerField()
    shipping_date = models.DateField()
    cancel_date = models.DateField()
    collection = models.ForeignKey(Collection)
    designer = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ManyToManyField(Item, blank=True)

    def __str__(self):
        return self.collection.season + str(self.number)
