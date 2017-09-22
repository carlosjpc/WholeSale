from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

from Disenador import models as designer_models
# Create your models here.
class ShowRoomInfo(models.Model):
    name = models.CharField(max_length=40)
    web_page = models.URLField(blank=True, null=True)
    State = models.CharField(max_length=12)
    Locality = models.CharField(max_length=22)
    Zip_Code = models.IntegerField()
    Street = models.CharField(max_length=120)
    Dept = models.CharField(max_length=30)
    Street2 = models.CharField(max_length=120, blank=True, null=True)
    phone1 = models.IntegerField()
    phone2 = models.IntegerField()
    
class Show_Room_Employee(models.Model):
    MANAGER = 'MG'
    SELLER = 'SE'
    ASSISTANT = 'JR'
    role_choices = (
        (MANAGER, 'Manager'),
        (SELLER, 'Seller'),
        (ASSISTANT, 'Assistant'),
    )
    role = models.CharField(max_length=2, choices=role_choices, default=ASSISTANT)
    designers = models.ManyToManyField(User, blank=True, related_name="clients")
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name="yo")

    def __str__(self):
        return self.user.username

class Store(models.Model):
    Store_Name = models.CharField(max_length=40, unique=True)
    web_page = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.Store_Name

    def get_absolute_url(self):
        return reverse('store_update', kwargs={'pk': self.pk})

class Contact(models.Model):
    role = models.CharField(max_length=40)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Address(models.Model):
    Country = models.CharField(max_length=12)
    State = models.CharField(max_length=12)
    Locality = models.CharField(max_length=22)
    Zip_Code = models.IntegerField()
    Street = models.CharField(max_length=120)
    Dept = models.CharField(max_length=30)
    Street2 = models.CharField(max_length=120, blank=True, null=True)
    Shipping_address = models.BooleanField()
    Sample_shipping_address = models.BooleanField(default=False)
    Billing_address = models.BooleanField(default=False)
    Reciever_name = models.CharField(max_length=20)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.Street

class Payment_Conditions(models.Model):
    description = models.CharField(max_length=60)
    credit = models.BooleanField(default=False)
    days_of_credit = models.IntegerField(default=0, blank=True, null=True)
    down_payment = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, blank=True, null=True)

    def __str__(self):
        return self.description

class PO(models.Model):
    PO_id = models.AutoField(primary_key=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now_add=True, blank=True)
    designer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="designer")
    seller = models.ForeignKey(User, blank=True, related_name="seller")
    collection = models.ForeignKey(designer_models.Collection, blank=True, null=True)
    delivery = models.ForeignKey(designer_models.Delivery, blank=True, null=True)
    payment_conditions = models.ForeignKey(Payment_Conditions, blank=True, null=True)
    shipping_date = models.DateField(blank=True)
    cancel_date = models.DateField(blank=True)
    accepted = models.BooleanField(default=False)
    shipping_co = models.CharField(max_length=20, blank=True, null=True)
    tracking_number = models.CharField(max_length=40, blank=True, null=True)
    signature = models.ImageField(upload_to=None, max_length=100, blank=True, null=True)
    total_value = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return '#' + str(self.PO_id) + ' Designer: ' + self.designer.username + ' / Store: ' + self.store.Store_Name + ' / $:' + str(self.total_value)

class PO_Entry(models.Model):
    po = models.ForeignKey(PO, on_delete=models.CASCADE)
    item = models.ForeignKey(designer_models.Item)
    unique_item = models.ForeignKey(designer_models.Item_Available_Sizes)
    qty = models.PositiveIntegerField()
    order = models.PositiveIntegerField(blank=True)
