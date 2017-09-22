from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.forms.widgets import SelectDateWidget
# imported to make the function 'brand' work
from django.shortcuts import get_object_or_404

from Disenador.models import (BaseItem, Item, Item_Available_Sizes, Color, Material, Extra_Attribute,
                            Size, Size_Group, Collection, Delivery, Designer_Profile, Designer_Employee)

from ShowRoom.models import PO

# function to filter forms according to user (if user is designer) or by the designer the user works for
def brand(user):
    if Designer_Profile.objects.filter(user=user).count() == 1:
        return user
    else:
        designer = get_object_or_404(User, pk=Designer_Employee.objects.filter(pk=user).values('works_for'))
        return designer

# Forms:
class ItemForm(forms.Form):
    item_field = forms.ModelMultipleChoiceField(queryset=Color.objects.none())
    def __init__(self, user):
        super(ItemForm, self).__init__()
        self.fields['item_field'].queryset = Color.objects.filter(designer=user)

class SkuForm(forms.Form):
    base_item = forms.ModelChoiceField(queryset=BaseItem.objects.none())
    color_or_print = forms.ModelMultipleChoiceField(queryset=Color.objects.none())
    material = forms.ModelMultipleChoiceField(queryset=Material.objects.none())
    size_group = forms.ModelMultipleChoiceField(queryset=Size_Group.objects.none())
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(SkuForm, self).__init__(*args, **kwargs)
        designer_obj = brand(self.request.user)
        self.fields['color_or_print'].queryset = Color.objects.filter(designer=designer_obj)
        self.fields['material'].queryset = Material.objects.filter(designer=designer_obj)
        self.fields['size_group'].queryset = Size_Group.objects.filter(designer=designer_obj)
        self.fields['base_item'].queryset = BaseItem.objects.filter(designer=designer_obj)

class DeliveryItemsForm(forms.Form):
    item = forms.ModelMultipleChoiceField(queryset=Item.objects.none())
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(DeliveryItemsForm, self).__init__(*args, **kwargs)
        designer_obj = brand(self.request.user)
        self.fields['item'].queryset = Item.objects.filter(designer=designer_obj)
        
##  Model Form
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

class Designer_ProfileForm(ModelForm):
    class Meta:
        model = Designer_Profile
        exclude = ['user']

class Employee_ProfileForm(ModelForm):
    class Meta:
        model = Designer_Employee
        exclude = ['user', 'works_for']

class ColorForm(ModelForm):
    class Meta:
        model = Color
        exclude = ['designer']

class MaterialForm(ModelForm):
    class Meta:
        model = Material
        exclude = ['designer']

class ExtraAttributeForm(ModelForm):
    class Meta:
        model = Extra_Attribute
        exclude = ['designer']

class CollectionForm(ModelForm):
    class Meta:
        model = Collection
        exclude = ['designer']

class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery
        exclude = ['designer', 'item']
        widgets = {
            'shipping_date': SelectDateWidget(),
            'cancel_date': SelectDateWidget()
        }

class DeliveryFormMC(ModelForm):
    class Meta:
        model = Delivery
        exclude = ['designer', 'collection', 'item']
        widgets = {
            'shipping_date': SelectDateWidget(),
            'cancel_date': SelectDateWidget()
        }

class SizeGroupForm(ModelForm):
    class Meta:
        model = Size_Group
        exclude = ['designer']

class SizeForm(ModelForm):
    class Meta:
        model = Size
        exclude = ['designer', 'group', 'sizePrice']

class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

class ItemFormMB(ModelForm):
    class Meta:
        model = Item
        exclude = ['clave', 'base', 'attribute']

class Designer_PO_Form(ModelForm):
    class Meta:
        model = PO
        fields = ('accepted',)

class Designer_PO_TrackingForm(ModelForm):
    class Meta:
        model = PO
        fields = ('shipping_co', 'tracking_number')
