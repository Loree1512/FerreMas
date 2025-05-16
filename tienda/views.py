from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Producto
# Create your views here.


def inicio(request):
    return render(request, 'tienda/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'tienda/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('registro')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo ya está registrado.')
            return redirect('registro')

        # Esta función guarda el password de forma segura
        User.objects.create_user(username=username, email=email, password=password)

        messages.success(request, 'Usuario registrado correctamente.')
        return redirect('inicio')  # O redirige donde tú quieras

    return render(request, 'tienda/registro.html')