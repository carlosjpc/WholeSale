from django.contrib import admin

# Register your models here.

from models import (BaseItem, Item, Item_Available_Sizes, Color, Material, Size_Group, Size, Extra_Attribute,
                    Collection, Delivery, Designer_Profile, Designer_Employee)

admin.site.register(Designer_Profile)
admin.site.register(Designer_Employee)
admin.site.register(BaseItem)
admin.site.register(Item)
admin.site.register(Item_Available_Sizes)
admin.site.register(Color)
admin.site.register(Material)
admin.site.register(Size)
admin.site.register(Size_Group)
admin.site.register(Extra_Attribute)
admin.site.register(Collection)
admin.site.register(Delivery)
