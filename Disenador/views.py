from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from datetime import datetime, timedelta

# app imports
from Disenador.models import (BaseItem, Item, Item_Available_Sizes, Color, Material, Size, Size_Group,
                            Extra_Attribute, Collection, Delivery, Designer_Profile, Designer_Employee)
from Disenador.forms import (ItemForm, ColorForm, MaterialForm, ExtraAttributeForm, CollectionForm, DeliveryItemsForm,
                            DeliveryForm, DeliveryFormMC, SizeForm, SizeGroupForm, ItemForm, ItemFormMB,
                            SkuForm, Employee_ProfileForm, UserForm, Designer_PO_Form, Designer_PO_TrackingForm)
from ShowRoom.models import PO, PO_Entry

# functions for decoraters to determine if a user can create / edit / delete or view:
def designer_check(user):
    if user:
        return user.groups.filter(name='Designer').count() == 1
    return False

def manager(user):
    if user:
        return Designer_Profile.objects.filter(user=user).count() == 1
    return False

def brand(user):
    if Designer_Profile.objects.filter(user=user).count() == 1:
        return user
    else:
        designer = get_object_or_404(User, pk=Designer_Employee.objects.filter(pk=user).values('works_for'))
        return designer

# normal views:
@login_required
@user_passes_test(manager)
def d_create_employee_user(request):
    if request.method == "POST":
        employeeform = UserForm(request.POST, instance=User())
        profileform = Employee_ProfileForm(request.POST, instance=Designer_Employee())
        if employeeform.is_valid() and profileform.is_valid():
            new_user = User.objects.create_user(**employeeform.cleaned_data)
            new_user.groups.add(Group.objects.get(name='Designer'))
            new_designer_profile = profileform.save(commit=False)
            new_designer_profile.user = new_user
            new_designer_profile.works_for = request.user
            new_designer_profile.save()
            return HttpResponseRedirect('main.html')
    employeeform = UserForm()
    profileform = Employee_ProfileForm()
    return render(request, 'Disenador/create_designer_employee_user.html', {'employeeform': employeeform, 'profileform': profileform, })

@login_required
def d_update_employee_user(request, pk):
    user = User.objects.get(pk=pk)
    employee = Designer_Employee.objects.get(pk=pk)
    if request.method == "POST":
        userform = UserForm(request.POST, instance=user)
        profileform = Employee_ProfileForm(request.POST, instance=employee)
        if employeeform.is_valid() and profileform.is_valid():
            user = userform.save()
            employee = profileform.save()
            return HttpResponseRedirect('main.html')
    employeeform = UserForm()
    profileform = Employee_ProfileForm()
    return render(request, 'Disenador/create_designer_employee_user.html', {'employeeform': employeeform, 'profileform': profileform, })

@login_required
@user_passes_test(designer_check)
def collection_detail(request, pk):
    designer_obj = brand(request.user)
    collection = get_object_or_404(Collection, pk=pk)
    if not collection.designer == designer_obj:
        return Http404
    deliveries = Delivery.objects.filter(collection=collection)
    return render(request, 'Disenador/collection_detail.html', {'collection': collection, 'deliveries': deliveries,})

@login_required
@user_passes_test(designer_check)
def delivery_create(request):
    designer_obj = brand(request.user)
    if request.method == "POST":
        form = DeliveryForm(request.POST, instance=Delivery())
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.designer = designer_obj
            new_form.save()
        return render(request, 'Disenador/collection_list.html', )
    else:
        form = DeliveryForm(instance=Delivery())
        form.fields['collection'].queryset = Collection.objects.filter(designer=designer_obj)
    return render(request, 'Disenador/create_edit_form.html', {'form': form,})

@login_required
@user_passes_test(designer_check)
def delivery_createMC(request, pk):
    designer_obj = brand(request.user)
    collection = get_object_or_404(Collection, pk=pk)
    if not collection.designer == designer_obj:
        return Http404
    if request.method == "POST":
        form = DeliveryFormMC(request.POST, instance=Delivery())
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.designer = designer_obj
            new_form.collection = collection
            new_form.save()
        return render(request, 'Disenador/collection_list.html', )
    else:
        form = DeliveryFormMC(instance=Delivery())
    return render(request, 'Disenador/create_edit_form.html', {'form': form,})

@login_required
@user_passes_test(designer_check)
def delivery_detail(request, pk):
    designer_obj = brand(request.user)
    delivery = get_object_or_404(Delivery, pk=pk)
    if not delivery.designer == designer_obj:
        return Http404
    items_pk = Delivery.objects.filter(pk=pk).values_list('item', flat=True)
    items = []
    for pk in items_pk:
        if pk != None:
            item = get_object_or_404(Item, pk=pk)
            items.append(item)
    return render(request, 'Disenador/delivery_detail.html', {'delivery': delivery, 'items': items,})

@login_required
@user_passes_test(designer_check)
def colors_create(request):
    designer_obj = brand(request.user)
    ColorFormSet = formset_factory(ColorForm, extra=1)
    if request.method == "POST":
        formset = ColorFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                new_form = form.save(commit=False)
                new_form.designer = designer_obj
                new_form.save()
        return HttpResponseRedirect('color_list')
    return render(request, 'Disenador/add_attribute.html', {'formset': ColorFormSet, 'Title': "Add colors and prints",})

@login_required
@user_passes_test(designer_check)
def materials_create(request):
    designer_obj = brand(request.user)
    MaterialFormSet = formset_factory(MaterialForm, extra=1)
    if request.method == "POST":
        formset = MaterialFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                new_form = form.save(commit=False)
                new_form.designer = designer_obj
                new_form.save()
        return HttpResponseRedirect('color_list')
    return render(request, 'Disenador/add_attribute.html', {'formset': MaterialFormSet, 'Title': "Add materials or the fabric composition you offer",})

@login_required
@user_passes_test(designer_check)
def size_chart_create(request):
    designer_obj = brand(request.user)
    SizeFormSet = formset_factory(SizeForm, extra=4)
    if request.method == "POST":
        formset = SizeFormSet(request.POST)
        gform = SizeGroupForm(request.POST, instance=Size_Group())
        if gform.is_valid():
            new_gform = gform.save(commit=False)
            new_gform.designer = designer_obj
            new_gform.save()
            if formset.is_valid():
                for form in formset:
                    new_form = form.save(commit=False)
                    new_form.designer = designer_obj
                    new_form.group = new_gform
                    new_form.save()
        return HttpResponseRedirect('color_list')
    gform = SizeGroupForm(instance=Size_Group())
    return render(request, 'Disenador/add_size_chart.html', {'gform': gform, 'formset': SizeFormSet,})

@login_required
@user_passes_test(designer_check)
def size_list(request):
    designer_obj = brand(request.user)
    sizes = Size.objects.filter(designer=designer_obj)
    groups = Size_Group.objects.filter(designer=designer_obj)
    return render(request, 'Disenador/size_list.html', {'sizes': sizes, 'groups': groups,})

@login_required
@user_passes_test(designer_check)
def item_list(request):
    designer_obj = brand(request.user)
    item_list = Item.objects.filter(designer=designer_obj)
    return render(request, 'Disenador/item_list.html', {'item_list': item_list,})

@login_required
@user_passes_test(designer_check)
def base_item_detail(request, pk):
    designer_obj = brand(request.user)
    base_item = get_object_or_404(BaseItem, pk=pk)
    if not base_item.designer == designer_obj:
        return Http404
    child_items = Item.objects.filter(base=base_item)
    return render(request, 'Disenador/base_item_detail.html', {'base_item': base_item, 'child_items': child_items,})

@login_required
@user_passes_test(designer_check)
def item_detail(request, pk):
    designer_obj = brand(request.user)
    item = get_object_or_404(Item, pk=pk)
    if not item.designer == designer_obj:
        return Http404
    base_item_pk = getattr(item, 'pk')
    base_item = get_object_or_404(BaseItem, pk=base_item_pk)
    return render(request, 'Disenador/item_detail.html', {'item': item, 'base_item': base_item, })

@login_required
@user_passes_test(designer_check)
def item_create(request):
    designer_obj = brand(request.user)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=Item())
        if form.is_valid:
            new_item = form.save(commit=False)
            new_item.designer = designer_obj
            new_item.save()
        return HttpResponseRedirect('color_list')
    form = ItemForm(instance=Item())
    form.fields['base'].queryset = BaseItem.objects.filter(designer=designer_obj)
    form.fields['color_or_print'].queryset = Color.objects.filter(designer=designer_obj)
    form.fields['material'].queryset = Material.objects.filter(designer=designer_obj)
    form.fields['size_group'].queryset = Size_Group.objects.filter(designer=designer_obj)
    return render(request, 'Disenador/create_edit_form.html', {'form': form,})

@login_required
@user_passes_test(designer_check)
def item_createMB(request, pk):
    base_item = get_object_or_404(BaseItem, pk=pk)
    designer_obj = brand(request.user)
    if not base_item.designer == designer_obj:
        return Http404
    if request.method == "POST":
        form = ItemFormMB(request.POST, instance=Item())
        if form.is_valid:
            new_item = form.save(commit=False)
            i = len(Item.objects.filter(base=base)) + 1
            new_item.clave = base_item.clave + "|" + str(i).zfill(2)
            new_item.base = base_item
            new_item.designer = designer_obj
            new_item.save()
        return HttpResponseRedirect('color_list')
    form = ItemFormMB(instance=Item())
    form.fields['color_or_print'].queryset = Color.objects.filter(designer=designer_obj)
    form.fields['material'].queryset = Material.objects.filter(designer=designer_obj)
    form.fields['size_group'].queryset = Size_Group.objects.filter(designer=designer_obj)
    return render(request, 'Disenador/create_edit_form.html', {'form': form,})

@login_required
@user_passes_test(designer_check)
def sku_builder(request):
    designer_obj = brand(request.user)
    if request.method == "POST":
        form = SkuForm(request.POST, request=request)
        if form.is_valid():
            base = form.cleaned_data['base_item']
            colors = form.cleaned_data['color_or_print']
            materials = form.cleaned_data['material']
            size_groups = form.cleaned_data['size_group']
            i = len(Item.objects.filter(base=base)) + 1
            for color in colors:
                for material in materials:
                    for size_group in size_groups:
                        if color.color_price:
                            colorPrice = color.color_price
                        else:
                            colorPrice = 0
                        if material.materialPrice:
                            materialPrice = material.materialPrice
                        else:
                            materialPrice = 0
                        price = base.BasePrice + colorPrice + materialPrice
                        clave = base.clave + "|" + str(i).zfill(2)
                        new_obj = Item(clave=clave, base=base, color_or_print=color, material=material, size_group=size_group, ItemPrice=price, designer=designer_obj)
                        new_obj.save()
                        sizes = Size.objects.filter(designer=designer_obj, group=size_group)
                        i += 1
                        for size in sizes:
                            sku = clave + str(size)
                            if size.sizePrice:
                                price = price + size.sizePrice
                            new_obj2 = Item_Available_Sizes(SKU=sku, item=new_obj, size=size, price=price)
                            new_obj2.save()
            url = reverse('base_item_detail', kwargs={'pk': base.pk})
            return HttpResponseRedirect(url)
        else:
            return HttpResponse("Upps! form is not valid")
    form = SkuForm(request=request)
    return render(request, 'Disenador/sku_builder.html', {'form': form,})

@login_required
@user_passes_test(designer_check)
def delivery_add_items(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    designer_obj = brand(request.user)
    if not delivery.designer == designer_obj:
        return Http404
    if request.method == "POST":
        form = DeliveryItemsForm(request.POST, request=request)
        if form.is_valid():
            items = form.cleaned_data['item']
            for item in items:
                delivery.item.add(item)
            url = reverse('delivery_detail', kwargs={'pk': delivery.pk})
            return HttpResponseRedirect(url)
    form = DeliveryItemsForm(request=request)
    return render(request, 'Disenador/create_edit_form.html', {'form': form,})

# CLASS BASED VIEWS
#collection views
class CollectionList(ListView):
    context_object_name = 'collections'
    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return Collection.objects.filter(designer=designer_obj)

class CollectionCreate(CreateView):
    model = Collection
    fields = ['season', 'year', 'name', 'description', 'lookbook']
    template_name = 'Disenador/create_edit_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        designer_obj = brand(self.request.user)
        obj.designer = designer_obj
        return super(CollectionCreate, self).form_valid(form)

class CollectionUpdate(UpdateView):
    model = Collection
    fields = ['season', 'year', 'name', 'description', 'lookbook']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('collection_list')

    def get_queryset(self):
        collection = super(CollectionUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        return collection.filter(designer=designer_obj)

class CollectionDelete(DeleteView):
    model = Collection
    template_name = 'Disenador/confirm_delete.html'
    success_url = reverse_lazy('collection_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is related 'works_for' or is owner by request.user """
        collection = super(CollectionDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not collection.designer == designer_obj:
            raise Http404
        return collection

#delivery views
class DeliveryList(ListView):
    context_object_name = 'deliveries'
    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return Delivery.objects.filter(designer=designer_obj)

class DeliveryUpdate(UpdateView):
    model = Delivery
    fields = ['number', 'shipping_date', 'cancel_date', 'collection']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('delivery_list')

    def get_queryset(self):
        delivery = super(DeliveryUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        return delivery.filter(designer=designer_obj)

class DeliveryDelete(DeleteView):
    model = Delivery
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('delivery_list')

    def get_object(self, queryset=None):
        delivery = super(DeliveryDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not delivery.designer == designer_obj:
            raise Http404
        return delivery

# color views
class ColorList(ListView):
    context_object_name = 'colors'
    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return Color.objects.filter(designer=designer_obj)

class ColorUpdate(UpdateView):
    model = Color
    fields = ['color_or_print', 'color_price', 'image']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('color_list')

    def get_queryset(self):
        color = super(ColorUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        return color.filter(designer=designer_obj)

class ColorDelete(DeleteView):
    model = Color
    template_name = 'Disenador/confirm_delete.html'
    success_url = reverse_lazy('color_list')

    def get_object(self, queryset=None):
        color = super(ColorDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not color.designer == designer_obj:
            raise Http404
        return color

class ColorDetail(DetailView):
    model = Color

    def get_queryset(self):
        color = super(ColorDetail, self).get_queryset()
        designer_obj = brand(self.request.user)
        return color.filter(designer=designer_obj)

# material views
class MaterialList(ListView):
    context_object_name = 'materials'
    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return Material.objects.filter(designer=designer_obj)

class MaterialUpdate(UpdateView):
    model = Material
    fields = ['name', 'materialPrice']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('material_list')

    def get_queryset(self):
        material = super(MaterialUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        return material.filter(designer=designer_obj)

class MaterialDelete(DeleteView):
    model = Material
    template_name = 'Disenador/confirm_delete.html'
    success_url = reverse_lazy('material_list')

    def get_object(self, queryset=None):
        material = super(MaterialDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not delivery.designer == designer_obj:
            raise Http404
        return material

class MaterialDetail(DetailView):
    model = Material

    def get_queryset(self):
        material = super(MaterialDetail, self).get_queryset()
        designer_obj = brand(self.request.user)
        return material.filter(designer=designer_obj)

# base item views
class BaseItemList(ListView):
    context_object_name = 'base_items'
    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return BaseItem.objects.filter(designer=designer_obj)

class BaseItemCreate(CreateView):
    model = BaseItem
    fields = ['clave', 'name', 'description', 'BasePrice']
    template_name = 'Disenador/create_edit_form.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        designer_obj = brand(self.request.user)
        obj.designer = designer_obj
        return super(BaseItemCreate, self).form_valid(form)

class BaseItemUpdate(UpdateView):
    model = BaseItem
    fields = ['clave', 'name', 'description', 'BasePrice']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('base_item_list')

    def get_queryset(self):
        baseitem = super(BaseItemUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        return baseitem.filter(designer=designer_obj)

class BaseItemDelete(DeleteView):
    model = BaseItem
    template_name = 'Disenador/confirm_delete.html'
    success_url = reverse_lazy('base_item_list')

    def get_object(self, queryset=None):
        base_item = super(BaseItemDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not delivery.designer == designer_obj:
            raise Http404
        return base_item

# item views
class ItemUpdate(UpdateView):
    model = Item
    fields = ['clave', 'base', 'color_or_print', 'material', 'attribute', 'size_group', 'ItemPrice', 'image']
    template_name = 'Disenador/create_edit_form.html'
    success_url = reverse_lazy('base_item_list')

    def get_queryset(self):
        item = super(ItemUpdate, self).get_queryset()
        designer_obj = brand(self.request.user)
        if not item.designer == designer_obj:
            raise Http404
        return item

class ItemDelete(DeleteView):
    model = Item
    template_name = 'Disenador/confirm_delete.html'
    success_url = reverse_lazy('base_item_list')

    def get_object(self, queryset=None):
        item = super(ItemDelete, self).get_object()
        designer_obj = brand(self.request.user)
        if not item.designer == designer_obj:
            raise Http404
        return item

# --------------------------------------------------------
# Views that link the Disenador app with the Showroom app
@login_required
def designer_ctrl_panel(request):
    designer_obj = brand(request.user)
    unaccepted_pos = PO.objects.filter(designer=designer_obj).filter(accepted=False)
    today = datetime.today()
    slash_date = datetime.today() - timedelta(days=10)
    recent_pos = PO.objects.filter(designer=designer_obj).filter(creation_date__range=(slash_date, today)).order_by('-creation_date')
    today_p15 = datetime.today() + timedelta(days=15)
    pos_close_to_cancel = PO.objects.filter(designer=designer_obj).filter(cancel_date__range=(today, today_p15)).filter(tracking_number=None).order_by('-cancel_date')
    pos_close_to_ship = PO.objects.filter(designer=designer_obj).filter(shipping_date__range=(today, today_p15)).filter(tracking_number=None).order_by('-cancel_date')
    return render(request, 'Disenador/ctrl_panel.html', {'designer_obj': designer_obj, 'unaccepted_pos': unaccepted_pos, 'recent_pos': recent_pos, 'pos_close_to_ship': pos_close_to_ship, 'pos_close_to_cancel': pos_close_to_cancel,})

class UnAccepted_POs(ListView):
    context_object_name = 'un_accepted_pos'

    def get_queryset(self):
        designer_obj = brand(self.request.user)
        return PO.objects.filter(designer=designer_obj).filter(accepted=False)

@login_required
def po_list_search(request):
    designer_obj = brand(request.user)
    pos_list = PO.objects.filter(designer=designer_obj)
    query = request.GET.get("q")
    if query:
        pos_list = pos_list.filter(
        Q(PO_id__icontains=query)|
        Q(store__Store_Name__icontains=query)|
        Q(collection__season__icontains=query)|
        Q(delivery__number__icontains=query)|
        Q(tracking_number__icontains=query)
        ).distinct()
    return render(request, 'Disenador/po_list.html', {'pos_list': pos_list,})

@login_required
def view_accept_po(request, pk):
    po = PO.objects.get(pk=pk)
    designer_obj = brand(request.user)
    if not po.designer == designer_obj:
        return Http404
    po_entries = PO_Entry.objects.filter(po=po)
    if request.method == "POST":
        form = Designer_PO_Form(request.POST, instance=PO())
        if form.is_valid:
            form.save()
            return HttpResponseRedirect('main.html')
    form = Designer_PO_Form()
    return render(request, 'Disenador/po_cform.html', {'po': po, 'po_entries': po_entries,'form': form,})

@login_required
def add_po_tracking(request, pk):
    po = PO.objects.get(pk=pk)
    designer_obj = brand(request.user)
    if not po.designer == designer_obj:
        return Http404
    po_entries = PO_Entry.objects.filter(po=po)
    if request.method == "POST":
        form = Designer_PO_TrackingForm(request.POST, instance=PO())
        if form.is_valid:
            form.save()
            return HttpResponseRedirect('main.html')
    form = Designer_PO_TrackingForm()
    return render(request, 'Disenador/po_cform.html', {'po': po, 'po_entries': po_entries,'form': form,})

@login_required
def POs_by_Collection(request, pk):
    designer_obj = brand(request.user)
    collection = get_object_or_404(Collection, pk=pk)
    if not collection.designer == designer_obj:
        return Http404
    collection_pos = PO.objects.filter(collection=collection)
    return render(request, 'Disenador/pos_by_collection.html', {'collection_pos': collection_pos, })

@login_required
def POs_by_Delivery(request, pk):
    designer_obj = brand(request.user)
    delivery = get_object_or_404(Delivery, pk=pk)
    if not delivery.designer == designer_obj:
        return Http404
    delivery_pos = PO.objects.filter(delivery=delivery)
    return render(request, 'Disenador/pos_by_delivery.html', {'delivery_pos': delivery_pos, })

# functions that work as widgets for the control panel view
def POs_to_Ship(request, days):
    designer_obj = brand(request.user)
    today = datetime.today()
    slash_date = datetime.today() + timedelta(days=days)
    pos = PO.objects.filter(designer=designer_obj).filter(shipping_date__range=(today, slash_date))
    return pos

def POs_Nearing_Cancel(request, days):
    designer_obj = brand(request.user)
    today = datetime.today()
    slash_date = datetime.today() + timedelta(days=days)
    pos = PO.objects.filter(designer=designer_obj).filter(cancel_date__range=(today, slash_date))
    return pos
