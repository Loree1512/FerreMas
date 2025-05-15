from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Producto

def inicio(request):
    return render(request, 'tienda/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})