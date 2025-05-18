from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('registro/', views.register_view, name='registro'),
    path('ubicacion/', views.mapa_ubicacion, name='mapa_ubicacion'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
