from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from Disenador import views
from Disenador.views import (CollectionCreate, CollectionUpdate, CollectionDelete, CollectionList, collection_detail,
                             DeliveryUpdate, DeliveryDelete, DeliveryList, delivery_detail,
                             colors_create, ColorUpdate, ColorDelete, ColorList, ColorDetail,
                             MaterialUpdate, MaterialDelete, MaterialList, MaterialDetail,
                             BaseItemList, BaseItemCreate, BaseItemUpdate, BaseItemDelete,
                             sku_builder,
                             item_list, item_create, item_createMB, ItemUpdate, ItemDelete,
                             UnAccepted_POs, POs_by_Collection, POs_by_Delivery, POs_to_Ship)


import debug_toolbar

urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^sku_builder/$', views.sku_builder, name='sku_builder'),
    # collection urls
    url(r'^collection_list/$', CollectionList.as_view() , name='collection_list'),
    url(r'^collection_add/$', CollectionCreate.as_view(), name='collection_add'),
    url(r'^collection_detail/(?P<pk>[0-9]+)/$', views.collection_detail, name='collection_detail'),
    url(r'^collection_update/(?P<pk>[0-9]+)/$', CollectionUpdate.as_view(), name='collection_update'),
    url(r'^collection_delete/(?P<pk>[0-9]+)/$', CollectionDelete.as_view(), name='collection_delete'),
    # delivery urls
    url(r'^delivery_list/$', DeliveryList.as_view() , name='delivery_list'),
    url(r'^delivery_add/$', views.delivery_create, name='delivery_add'),
    url(r'^delivery_add/(?P<pk>[0-9]+)/$', views.delivery_createMC, name='delivery_add_mc'),
    url(r'^delivery_detail/(?P<pk>[0-9]+)/$', views.delivery_detail, name='delivery_detail'),
    url(r'^delivery_update/(?P<pk>[0-9]+)/$', DeliveryUpdate.as_view(), name='delivery_update'),
    url(r'^delivery_delete/(?P<pk>[0-9]+)/$', DeliveryDelete.as_view(), name='delivery_delete'),
    url(r'^delivery_add_items/(?P<pk>[0-9]+)/$', views.delivery_add_items, name='delivery_add_items'),
    # color urls
    url(r'^color_list/$', ColorList.as_view() , name='color_list'),
    url(r'^color_add/$', views.colors_create, name='colors_add'),
    url(r'^color_detail/(?P<pk>[0-9]+)/$', ColorDetail.as_view(), name='color_detail'),
    url(r'^color_update/(?P<pk>[0-9]+)/$', ColorUpdate.as_view(), name='color_update'),
    url(r'^color_delete/(?P<pk>[0-9]+)/$', ColorDelete.as_view(), name='color_delete'),
    # material urls
    url(r'^material_list/$', MaterialList.as_view() , name='material_list'),
    url(r'^material_add/$', views.materials_create, name='materials_add'),
    url(r'^material_detail/(?P<pk>[0-9]+)/$', MaterialDetail.as_view(), name='material_detail'),
    url(r'^material_update/(?P<pk>[0-9]+)/$', MaterialUpdate.as_view(), name='material_update'),
    url(r'^material_delete/(?P<pk>[0-9]+)/$', MaterialDelete.as_view(), name='material_delete'),
    # size urls
    url(r'^size_list/$', views.size_list, name='size_list'),
    url(r'^size_chart_add/$', views.size_chart_create, name='size_chart_create'),
    # base item urls
    url(r'^base_item_list/$', BaseItemList.as_view() , name='base_item_list'),
    url(r'^base_item_add/$', BaseItemCreate.as_view(), name='base_item_add'),
    url(r'^base_item_detail/(?P<pk>[0-9]+)/$', views.base_item_detail, name='base_item_detail'),
    url(r'^base_item_update/(?P<pk>[0-9]+)/$', BaseItemUpdate.as_view(), name='base_item_update'),
    url(r'^base_item_delete/(?P<pk>[0-9]+)/$', BaseItemDelete.as_view(), name='base_item_delete'),
    # items urls
    url(r'^item_list/$', views.item_list, name='item_list'),
    url(r'^item_add/$', views.item_create, name='item_add'),
    url(r'^item_add_mb/(?P<pk>[0-9]+)/$', views.item_createMB, name='item_add_mb'),
    url(r'^item_detail/(?P<pk>[0-9]+)/$', views.item_detail, name='item_detail'),
    url(r'^item_update/(?P<pk>[0-9]+)/$', ItemUpdate.as_view(), name='item_update'),
    url(r'^item_delete/(?P<pk>[0-9]+)/$', ItemDelete.as_view(), name='item_delete'),
    # employees urls
    url(r'^employee_user_create/$', views.d_create_employee_user, name='d_employee_user_create'),
    url(r'^employee_update/(?P<pk>[0-9]+)/$', views.d_update_employee_user , name="d_employee_update"),
    # urls for views that link the ShowRoom app with the Disenador app
    url(r'^ctrl_panel/$', views.designer_ctrl_panel, name='designer_ctrl_panel'),
    url(r'^pos_list_search/$', views.po_list_search, name='po_list_search'),
    url(r'^unaccepted_pos_list/$', UnAccepted_POs.as_view(), name='unaccepted_pos_list'),
    url(r'^view_accept_po/(?P<pk>[0-9]+)/$', views.view_accept_po, name="view_accept_po"),
    url(r'^add_po_tracking/(?P<pk>[0-9]+)/$', views.add_po_tracking, name="add_po_tracking"),
    url(r'^pos_by_collection/(?P<pk>[0-9]+)/$', views.POs_by_Collection, name='pos_by_collection'),
    url(r'^pos_by_delivery/(?P<pk>[0-9]+)/$', views.POs_by_Delivery, name='pos_by_delivery'),
    url(r'^pos_by_ship_in/(?P<days>[0-9]+)/days/$', views.POs_to_Ship, name='pos_to_ship_in_x_days'),
]
