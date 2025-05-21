from django.contrib import admin
from .models import Producto, Perfil, Orden, ItemOrden
# Register your models here.


admin.site.register(Producto)
class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username',)


class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email', 'total', 'fecha')
    inlines = [ItemOrdenInline]

admin.site.register(Orden, OrdenAdmin)