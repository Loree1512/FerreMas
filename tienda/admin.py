from django.contrib import admin
from .models import Producto, Orden, ItemOrden
# Register your models here.


admin.site.register(Producto)
class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0

class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email', 'total', 'fecha')
    inlines = [ItemOrdenInline]

admin.site.register(Orden, OrdenAdmin)