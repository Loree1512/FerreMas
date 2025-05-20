from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('registro/', views.register_view, name='registro'),
    path('ubicacion/', views.mapa_ubicacion, name='mapa_ubicacion'),
    path('login/', views.login_view, name='login'),
    path('panel/inicio/', views.admin_inicio_view, name='admin_inicio'),
    path('panel/inicio/', views.admin_inicio_view, name='admin_inicio'),
    path('panel/bodeguero/', views.bodeguero_inicio, name='bodeguero_inicio'),
    path('panel/contador/', views.contador_inicio, name='contador_inicio'), 
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contacto, name='contacto'),
    path('categoria/<str:categoria>/', views.productos_por_categoria, name='productos_categoria'),
    path('checkout/', views.checkout_view, name='checkout'),  # MOVIDO DENTRO DE LA LISTA
    path('api/orden/', views.registrar_orden, name='registrar_orden'),  # MOVIDO DENTRO DE LA LISTA
    path('orden/actualizar/<int:orden_id>/', views.actualizar_estado_orden, name='actualizar_estado_orden'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)