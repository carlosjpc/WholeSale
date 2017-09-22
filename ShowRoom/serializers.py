from django.contrib.auth.models import User, Group
from rest_framework import serializers

from Disenador.models import Collection, Delivery, BaseItem, Item, Color, Material, Size_Group, Size_Group
from ShowRoom.models import Store, PO

class DesignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'pk',)

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('season', 'pk',)

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ('number', 'pk',)
