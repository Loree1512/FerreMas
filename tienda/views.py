from django.shortcuts import render

# Create your views here.
from .models import Producto

def inicio(request):
    return render(request, 'tienda/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})