from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from tienda.views import actualizar_estado_bodega

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('registro/', views.register_view, name='registro'),
    path('ubicacion/', views.mapa_ubicacion, name='mapa_ubicacion'),
    path('login/', views.login_view, name='login'),
    path('panel/inicio/', views.admin_inicio_view, name='admin_inicio'),
    path('panel/bodeguero/', views.bodeguero_inicio, name='bodeguero_inicio'),
    path('panel/contador/', views.contador_inicio, name='contador_inicio'), 
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contacto, name='contacto'),
    path('categoria/<str:categoria>/', views.productos_por_categoria, name='productos_categoria'),
    path('checkout/', views.checkout_view, name='checkout'),  # MOVIDO DENTRO DE LA LISTA
    path('api/orden/', views.registrar_orden, name='registrar_orden'),  # MOVIDO DENTRO DE LA LISTA
    path('orden/actualizar/<int:orden_id>/', views.actualizar_estado_orden, name='actualizar_estado_orden'),
    path('orden/<int:orden_id>/procesar/', views.procesar_orden, name='procesar_orden'),
    path('orden/actualizar/<int:orden_id>/', views.actualizar_estado_bodega, name='actualizar_estado_bodega'),
    path('orden/validar/<int:orden_id>/', views.actualizar_estado_contador, name='actualizar_estado_contador'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('panel/ordenes/', views.admin_ordenes_view, name='admin_ordenes'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('checkout/datos/', views.formulario_cliente, name='formulario_cliente'),
    path('bodeguero/productos/', views.bodeguero_productos, name='bodeguero_productos'),
    path('bodeguero/ordenes/', views.ordenes_bodeguero, name='bodeguero_ordenes'),
    path('admin/usuarios/', views.crear_usuario, name='admin_usuarios'),
    path('producto/<int:producto_id>/stock/', views.actualizar_stock, name='actualizar_stock'),
    path('producto/<int:producto_id>/disponible/', views.actualizar_disponible, name='actualizar_disponible'),
    path('panel/bodeguero/orden/<int:orden_id>/actualizar/', views.actualizar_estado_bodega, name='actualizar_estado_bodega'),
    path('panel/bodeguero/limpiar/', views.limpiar_historial_bodeguero, name='limpiar_historial_bodeguero'),
    path('panel/vendedor/orden/<int:orden_id>/actualizar/', views.actualizar_estado_vendedor, name='actualizar_estado_vendedor'),





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)