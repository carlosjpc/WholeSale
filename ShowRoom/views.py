from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.forms.formsets import formset_factory
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views import generic
from datetime import datetime, timedelta

# REST_FRAMEWORK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import generics

# GRAPHOS
from graphos.sources.model import ModelDataSource
from graphos.renderers import gchart

# Internal imports
from ShowRoom.models import Store, Contact, Address, Payment_Conditions, Show_Room_Employee, PO, PO_Entry
from ShowRoom.forms import StoreForm, ContactForm, AddressForm, PO_Form, UserForm, EmployeeForm
from ShowRoom.serializers import DesignerSerializer, CollectionSerializer, DeliverySerializer
from Disenador.models import (Collection, Delivery, Item, Designer_Profile, BaseItem, Color, Material,
                            Size_Group, Size, Item_Available_Sizes)
from Disenador.forms import Designer_ProfileForm

# Create your views here.

def role_check(user):
    employee = get_object_or_404(Show_Room_Employee, pk=user.pk)
    role = getattr(employee, 'role')
    return role


@login_required
def ctrl_panel_manager(request):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=30)
    recent_pos = PO.objects.filter(creation_date__range=(slash_date, today)).order_by('-creation_date')
    today_m3 = datetime.today() - timedelta(days=3)
    unaccepted_recent_pos = PO.objects.filter(accepted=False).filter(creation_date__range=(slash_date, today_m3)).order_by('-creation_date')[:10]
    today_p5 = datetime.today() + timedelta(days=5)
    pos_close_to_cancel = PO.objects.filter(cancel_date__range=(today, today_p5)).filter(tracking_number=None).order_by('-cancel_date')
    data_source = ModelDataSource(recent_pos, fields=['creation_date', 'total_value'])
    chart = gchart.LineChart(data_source, height=350, width=650, options={'title': 'Recent Sales:'})
    return render(request, 'showroom/ctrl_panel.html', {'chart': chart, 'recent_pos': recent_pos, 'unaccepted_recent_pos': unaccepted_recent_pos, 'pos_close_to_cancel': pos_close_to_cancel,})


@login_required
def ctrl_panel_seller(request):
    role = role_check(request.user)
    if not role == 'SE':
        return Http404
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=30)
    recent_pos = PO.objects.filter(seller=request.user).filter(creation_date__range=(slash_date, today)).order_by('-creation_date')[:10]
    today_m3 = datetime.today() - timedelta(days=3)
    unaccepted_recent_pos = PO.objects.filter(seller=request.user).filter(accepted=False).filter(creation_date__range=(slash_date, today_m3)).order_by('-creation_date')[:10]
    today_p5 = datetime.today() + timedelta(days=5)
    pos_close_to_cancel = PO.objects.filter(seller=request.user).filter(cancel_date__range=(today, today_p5)).filter(tracking_number=None).order_by('-cancel_date')
    return render(request, 'showroom/ctrl_panel_manager.html', {'recent_pos': recent_pos, 'unaccepted_recent_pos': unaccepted_recent_pos, 'pos_close_to_cancel': pos_close_to_cancel,})

@login_required
def create_designer_user(request):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    if request.method == "POST":
        designerform = UserForm(request.POST, instance=User())
        profileform = Designer_ProfileForm(request.POST, instance=Designer_Profile())
        if form.is_valid() and profileform.is_valid():
            new_user = User.objects.create_user(**designerform.cleaned_data)
            new_designer_profile = profileform.save(commit=False)
            new_designer_profile.user = new_user
            new_designer_profile.save()
            return HttpResponseRedirect('/designer/collections/deliveries/')
    designerform = UserForm()
    profileform = Designer_ProfileForm()
    return render(request, 'showroom/create_designer_user.html', {'designerform': designerform, 'profileform': profileform, })

@login_required
def create_employee_user(request):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    if request.method == "POST":
        userform = UserForm(request.POST, instance=User())
        employeeform = EmployeeForm(request.POST, instance=Show_Room_Employee())
        if userform.is_valid() and employeeform.is_valid():
            new_user = User.objects.create_user(**userform.cleaned_data)
            new_employee = employeeform.save(commit=False)
            new_employee.user = new_user
            new_employee.save()
            employeeform.save_m2m()
            return HttpResponseRedirect('/employee_list/')
    userform = UserForm()
    employeeform = EmployeeForm()
    employeeform.fields['designers'].queryset = User.objects.filter(groups__name='Designer')
    return render(request, 'showroom/create_employee_user.html', {'userform': userform, 'employeeform': employeeform, })

@login_required
def update_employee_user(request, pk):
    user = User.objects.get(pk=pk)
    employee = Show_Room_Employee.objects.get(pk=pk)
    if request.method == "POST":
        userform = UserForm(request.POST, instance=user)
        profileform = EmployeeForm(request.POST, instance=employee)
        if userform.is_valid() and profileform.is_valid():
            user = userform.save()
            employee = profileform.save()
            return HttpResponseRedirect('/employee_list/')
    employeeform = UserForm(instance=user)
    profileform = EmployeeForm(instance=employee)
    return render(request, 'Disenador/create_designer_employee_user.html', {'employeeform': employeeform, 'profileform': profileform, })

@login_required
def add_store(request):
    role = role_check(request.user)
    if not (role == 'MG' or role == 'SE'):
        return Http404
    AddressFormSet = formset_factory(AddressForm, extra=1)
    if request.method == "POST":
        sform = StoreForm(request.POST, instance=Store())
        cform = ContactForm(request.POST, instance=Contact())
        formset = AddressFormSet(request.POST)
        if sform.is_valid():
            new_store = sform.save(commit=False)
            new_store.save()
            if cform.is_valid():
                new_contact = cform.save(commit=False)
                new_contact.store = new_store
                new_contact.save()
                if formset.is_valid():
                    for form in formset:
                        new_address = form.save(commit=False)
                        new_address.store = new_store
                        new_address.save()
                return HttpResponseRedirect('/store_list/')
    else:
        sform = StoreForm(instance=Store())
        cform = ContactForm(instance=Contact())
        aform = AddressForm(instance=Address())
    return render(request, 'showroom/newStore.html', {'store_form': sform, 'contact_form': cform, 'formset': AddressFormSet, })

@login_required
def store_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    contactList = Contact.objects.filter(store=store)
    addressList = Address.objects.filter(store=store)
    return render(request, 'showroom/store_detail.html', {'store': store, 'contactList': contactList, 'addressList': addressList, })

@login_required
def Store_Contact_Create(request, pk):
    role = role_check(request.user)
    if not (role == 'MG' or role == 'SE'):
        return Http404
    if request.method == "POST":
        store = get_object_or_404(Store, pk=pk)
        cform = ContactForm(request.POST, instance=Contact())
        if cform.is_valid():
            new_contact = cform.save(commit=False)
            new_contact.store = store
            new_contact.save()
            return HttpResponseRedirect('showroom/store_list/')
    else:
        cform = ContactForm(request.POST, instance=Contact())
    return render(request, 'create_edit_form.html', {'form': cform, })

@login_required
def PO_formset_populate(request, delivery_pk, po_pk):
    role = role_check(request.user)
    if not (role == 'MG' or role == 'SE'):
        return Http404
    po = get_object_or_404(PO, pk=po_pk)
    PO_FormSet = formset_factory(PO_Form, extra=1)
    if request.method == "POST":
        formset = PO_FormSet(request.POST, form_kwargs={'delivery_pk': delivery_pk})
        if formset.is_valid():
            delivery = get_object_or_404(Delivery, pk=delivery_pk)
            designer = get_object_or_404(User, username=delivery.designer)
            for form in formset:
                base_item = form.cleaned_data['base_item']
                base_obj = BaseItem.objects.get(designer=designer, name=base_item)
                color_or_print = form.cleaned_data['color_or_print']
                color_obj = Color.objects.get(designer=designer, color_or_print=color_or_print)
                material = form.cleaned_data['material']
                material_obj = Material.objects.get(designer=designer, name=material)
                size_group = form.cleaned_data['size_group']
                size_g_obj = Size_Group.objects.get(designer=designer, group_name=size_group)
                try:
                    item = Item.objects.get(base=base_obj, color_or_print=color_obj, material=material_obj, size_group=size_g_obj)
                except Item.DoesNotExist:
                    return HttpResponse('<h1>Item does not exists found</h1>')
                except Item.MultipleObjectsReturned:
                    return HttpResponse('<h1>Multiple objs</h1>')
                qty = []
                qty.append(form.cleaned_data['qty_size1'])
                qty.append(form.cleaned_data['qty_size2'])
                qty.append(form.cleaned_data['qty_size3'])
                qty.append(form.cleaned_data['qty_size4'])
                qty.append(form.cleaned_data['qty_size5'])
                i = 0
                for size in Size.objects.filter(group=size_g_obj):
                    unique_item = Item_Available_Sizes.objects.get(item=item, size=size)
                    if qty[i] != None:
                        new_entry = PO_Entry(po=po, item=item, unique_item=unique_item, qty=qty[i], order=i)
                        new_entry.save()
                    else:
                        return HttpResponse('<h1>Object not found/h1>')
                    i += 1
        else:
            return render(request, 'showroom/po_populate.html', {'formset': formset,})
    formset = PO_FormSet(form_kwargs={'delivery_pk': delivery_pk})
    return render(request, 'showroom/po_populate.html', {'formset': formset,})

@login_required
def po_detail (request, pk):
    po = get_object_or_404(PO, pk=pk)
    store = Store.objects.get(Store_Name=getattr(po, 'store'))
    try:
        addresses = Address.objects.filter(store=store)
    except Item.DoesNotExist:
        addresses = empty
    po_entries = PO_Entry.objects.filter(po=po)
    items = []
    qty = []
    sub_Total = []
    for po_entry in PO_Entry.objects.filter(po=po):
        item = Item.objects.get(designer=po.designer ,clave=po_entry.item)
        if item not in items:
            items.append(item)
            qty.append(po_entry.qty)
            sub_Total.append(po_entry.qty * item.ItemPrice)
        else:
            x = items.index(item)
            qty[x] = qty[x] + po_entry.qty
            sub_Total[x] = qty[x] * item.ItemPrice
    Total = sum(sub_Total)
    return render(request, 'showroom/po_detail.html', {'po': po, 'po_entries': po_entries, 'items': items, 'qty': qty, 'sub_Total': sub_Total, 'addresses': addresses, 'Total': Total, })

@login_required
def my_new_pos(request, days):
    role = role_check(request.user)
    if not (role == 'MG' or role == 'SE'):
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(seller=request.user).filter(creation_date__range=(slash_date, today))
    return render(request, 'showroom/my_new_pos.html', {'recent_pos': recent_pos,})

@login_required
def new_pos(request, days):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(creation_date__range=(slash_date, today)).order_by('seller')
    return render(request, 'showroom/new_pos.html', {'recent_pos': recent_pos,})

@login_required
def new_pos_seller(request, seller_pk, days):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(seller=seller_pk).filter(creation_date__range=(slash_date, today))
    return render(request, 'showroom/new_pos.html', {'recent_pos': recent_pos,})

@login_required
def new_pos_seller_designer(request, seller_pk, designer_pk, days):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(seller=seller_pk).filter(designer=designer_pk).filter(creation_date__range=(slash_date, today))
    return render(request, 'showroom/new_pos.html', {'recent_pos': recent_pos,})

@login_required
def unaccepted_pos(request, days):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(accepted=False)
    return render(request, 'showroom/.html', {'recent_pos': recent_pos,})

@login_required
def my_unaccepted_pos(request, days):
    role = role_check(request.user)
    if not (role == 'MG' or role == 'SE'):
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.filter(accepted=False)
    return render(request, 'showroom/.html', {'recent_pos': recent_pos,})

@login_required
def unaccepted_pos_seller(request, seller_pk, days):
    role = role_check(request.user)
    if not role == 'MG':
        return Http404
    days = int(days)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=days)
    recent_pos = PO.objects.fliter(seller=seller_pk).filter(accepted=False)
    return render(request, 'showroom/.html', {'recent_pos': recent_pos,})

#Rest Framework Views
class DesignerList(generics.ListAPIView):
    serializer_class = DesignerSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Designer')

class CollectionList_4D(generics.ListAPIView):
    serializer_class = CollectionSerializer

    def get_queryset(self):
        designer_pk = self.kwargs['designer_pk']
        designer = get_object_or_404(User, pk=designer_pk)
        return Collection.objects.filter(designer=designer)

class DeliveryList_4DC(generics.ListAPIView):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        collection_pk = self.kwargs['collection_pk']
        collection = get_object_or_404(Collection, pk=collection_pk)
        return Delivery.objects.filter(collection=collection)

#Class Based Views
class StoreList(generic.ListView):
    template_name = 'showroom/store_list.html'
    context_object_name = 'all_stores'

    def get_queryset(self):
        return Store.objects.all().order_by('Store_Name')

class StoreCreate(CreateView):
    model = Store
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'

class StoreUpdate(UpdateView):
    model = Store
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'
    success_url = reverse_lazy('store_list')

class StoreDelete(DeleteView):
    model = Store
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('store_list')

class DesignerUpdate(UpdateView):
    model = Designer_Profile
    fields = ['bio', 'created_in', 'style']
    template_name = 'showroom/create_edit_form.html'
    success_url = reverse_lazy('designers_collections_d')

class DesignerDelete(DeleteView):
    model = Designer_Profile
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('designers_collections_d')

class ContactCreate(CreateView):
    model = Contact
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'

class ContactUpdate(UpdateView):
    model = Contact
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'

class ContactDelete(DeleteView):
    model = Contact
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('store_list')

class AddressCreate(CreateView):
    model = Address
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'

class AddressUpdate(UpdateView):
    model = Address
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'

class AddressDelete(DeleteView):
    model = Address
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('store_list')

class Payment_ConditionsList(generic.ListView):
    template_name = 'showroom/payment_conditions_list.html'
    context_object_name = 'payment_conditions'

    def get_queryset(self):
        return Payment_Conditions.objects.all().order_by('description')

class Payment_ConditionsCreate(CreateView):
    model = Payment_Conditions
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'
    success_url = reverse_lazy('payment_condition_list')

class Payment_ConditionsUpdate(UpdateView):
    model = Payment_Conditions
    fields = '__all__'
    template_name = 'showroom/create_edit_form.html'
    success_url = reverse_lazy('payment_condition_list')

class Payment_ConditionsDelete(DeleteView):
    model = Payment_Conditions
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('payment_condition_list')

class EmployeeList(generic.ListView):
    template_name = 'showroom/employee_list.html'
    context_object_name = 'employies'

    def get_queryset(self):
        return Show_Room_Employee.objects.all().order_by('role')

class EmployeeDelete(DeleteView):
    model = User
    template_name = 'showroom/confirm_delete.html'
    success_url = reverse_lazy('employee_list')

class PO_Update(UpdateView):
    model = PO
    fields = ['store', 'designer', 'collection', 'delivery', 'payment_conditions', 'shipping_date', 'cancel_date', 'signature', 'total_value',]
    template_name = 'showroom/create_edit_form.html'

    def get_object(self, queryset=None):
        obj = PO.objects.get(PO_id=self.kwargs['pk'])
        obj.accepted = False
        return obj

# --------------------------------------------------------
# Views that link the ShowRoom app with the Disenador app

@login_required
def designers_collections_d(request):
    designers = []
    for profile in Designer_Profile.objects.all():
        designer = User.objects.get(pk=getattr(profile.user, 'pk'))
        designers.append(designer)
    collections = Collection.objects.all().order_by('-year')
    deliveries = Delivery.objects.all()
    return render(request, 'showroom/designer_collection_delivery_detail.html', {'designers': designers, 'collections': collections, 'deliveries': deliveries,})

@login_required
def designer_detail(request, pk):
    designer = Designer_Profile.objects.get(pk=pk)
    return render(request, 'showroom/designer_profile_detail.html', {'designer': designer,})

@login_required
def collection_list_4D(request, pk):
    designer = User.objects.get(pk=pk)
    collections = Collection.objects.filter(designer=designer)
    return render(request, 'showroom/collection_list_4D.html', {'collections': collections,})

@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    deliveries = Delivery.objects.filter(collection=collection)
    return render(request, 'showroom/collection_detail.html', {'collection': collection, 'deliveries': deliveries,})

@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    items_pk = Delivery.objects.filter(pk=pk).values_list('item', flat=True)
    items = []
    for pk in items_pk:
        if pk != None:
            item = Item.objects.get(pk=pk)
            items.append(item)
    return render(request, 'showroom/delivery_detail.html', {'delivery': delivery, 'items':items,})
