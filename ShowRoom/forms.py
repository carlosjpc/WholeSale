from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from Disenador.models import Item_Available_Sizes, Item, BaseItem, Color, Material, Size_Group, Delivery
from models import Store, Contact, Address, Show_Room_Employee

class PO_Form(forms.Form):
    base_item = forms.ChoiceField('')
    color_or_print = forms.ChoiceField('')
    material = forms.ChoiceField('')
    size_group = forms.ChoiceField('')
    qty_size1 = forms.IntegerField(required = False)
    qty_size2 = forms.IntegerField(required = False)
    qty_size3 = forms.IntegerField(required = False)
    qty_size4 = forms.IntegerField(required = False)
    qty_size5 = forms.IntegerField(required = False)

    def __init__(self, *args, **kwargs):
        delivery_pk = kwargs.pop('delivery_pk')
        self.delivery_pk = delivery_pk
        super(PO_Form, self).__init__(*args, **kwargs)
        delivery = get_object_or_404(Delivery, pk=self.delivery_pk)
        designer = get_object_or_404(User, username=delivery.designer)
        items_pk = Delivery.objects.filter(pk=self.delivery_pk).values_list('item', flat=True)
        items = []
        baseItem_choices = []
        color_choices = []
        material_choices = []
        sizeGroup_choices = []
        for pk in items_pk:
            item = get_object_or_404(Item, pk=pk)
            items.append(item)
            item_base = BaseItem.objects.get(designer=designer, name=getattr(item, 'base'))
            if not (item_base, item_base) in baseItem_choices:
                baseItem_choices.append((item_base, item_base),)
            item_color = Color.objects.get(designer=designer, color_or_print=getattr(item, 'color_or_print'))
            if (item_color, item_color) not in color_choices:
                color_choices.append((item_color, item_color),)
            item_material = Material.objects.get(designer=designer, name=getattr(item, 'material'))
            if (item_material, item_material) not in material_choices:
                material_choices.append((item_material, item_material),)
            item_size_g = Size_Group.objects.get(designer=designer, group_name=getattr(item, 'size_group'))
            if (item_size_g, item_size_g) not in sizeGroup_choices:
                sizeGroup_choices.append((item_size_g, item_size_g),)
        self.fields['base_item'].choices = baseItem_choices
        self.fields['color_or_print'].choices = color_choices
        self.fields['material'].choices = material_choices
        self.fields['size_group'].choices = sizeGroup_choices

 #'notes': forms.Textarea(attrs={'rows':4, 'cols':25}),
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

class EmployeeForm(ModelForm):
    class Meta:
        model = Show_Room_Employee
        fields = ('role', 'designers')

class StoreForm(ModelForm):
  class Meta:
      model = Store
      fields = '__all__'

class ContactForm(ModelForm):
  class Meta:
      model = Contact
      exclude = ('store',)

class AddressForm(ModelForm):
  class Meta:
      model = Address
      exclude = ('store',)
