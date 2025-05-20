from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('registro/', views.register_view, name='registro'),
    path('ubicacion/', views.mapa_ubicacion, name='mapa_ubicacion'),
    path('login/', views.login_view, name='login'),
    path('panel/inicio/', views.admin_inicio_view, name='admin_inicio'),
    path('logout/', views.logout_view, name='logout'),
    path('contacto/', views.contacto, name='contacto'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/orden/', views.registrar_orden, name='registrar_orden'),
]
