from django.contrib import admin
from ShowRoom.models import Store, Contact, Address, PO, PO_Entry, Show_Room_Employee, Payment_Conditions

# Register your models here.
admin.site.register(PO)
admin.site.register(PO_Entry)
admin.site.register(Show_Room_Employee)
admin.site.register(Store)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Payment_Conditions)
