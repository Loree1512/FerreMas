from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Orden, ItemOrden
from .forms import ProductoForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# Create your views here.


def inicio(request):
    return render(request, 'tienda/inicio.html')

@login_required
def inicio_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_inicio')
    return render(request, 'tienda/inicio.html')

@login_required
def admin_inicio_view(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('inicio')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_inicio')
    else:
        form = ProductoForm()

    productos = Producto.objects.all()
    return render(request, 'tienda/admin_inicio.html', {'form': form, 'productos': productos})


@login_required
def bodeguero_inicio(request):
    ordenes = Orden.objects.all().order_by('-fecha')
    return render(request, 'tienda/bodeguero/inicio.html', {'ordenes': ordenes})


@login_required
def contador_inicio(request):
    ordenes = Orden.objects.filter(metodo_pago='transferencia')
    return render(request, 'tienda/contador/inicio.html', {'ordenes': ordenes})

def checkout_view(request):
    return render(request, 'tienda/checkout.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige al login después de cerrar sesión

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

def mapa_ubicacion(request):
    """Vista para mostrar la ubicación de la ferretería en el mapa."""
    context = {
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'titulo': 'Nuestra Ubicación',
        'ubicacion': {
            'lat': -33.024,  # Reemplaza con la latitud de tu ferretería
            'lng': -71.552,  # Reemplaza con la longitud de tu ferretería
            'nombre': 'FerreTools',
            'direccion': 'Av. Principal 1234, Ciudad',
            'telefono': '+56 2 2123 4567',
            'horario': 'Lun-Sáb 8:30 - 19:00'
        }
    }
    return render(request, 'tienda/mapa_ubicacion.html', context)
def contacto(request):
    return render(request, 'tienda/contacto.html')

def contact_send(request):
    if request.method == 'POST':
        # Procesar formulario
        nombre = request.POST.get('name')
        email = request.POST.get('email')
        # ... procesar otros campos
        
        # Añadir mensaje de confirmación
        messages.success(request, 'Tu mensaje ha sido enviado correctamente.')
        
    return redirect('contacto')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                perfil = getattr(user, 'perfil', None)
                if perfil:
                    if perfil.rol == 'bodeguero':
                        return redirect('bodeguero_inicio')
                    elif perfil.rol == 'contador':
                        return redirect('contador_inicio')
                return redirect('admin_inicio')  # Vendedor u otro staff
            else:
                return redirect('inicio')  # Usuario común
        else:
            return render(request, 'tienda/login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'tienda/login.html')

def productos_por_categoria(request, categoria):
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'tienda/productos_categoria.html', {
        'productos': productos,
        'categoria_actual': categoria
    })
@csrf_exempt
def registrar_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            total = data.get('total')
            nombre = data.get('nombre')
            email = data.get('email')

            orden = Orden.objects.create(
                nombre_cliente=nombre,
                email=email,
                total=total,
                usuario=request.user if request.user.is_authenticated else None
            )

            for item in carrito:
                try:
                    producto = Producto.objects.get(id=item['id'])
                    ItemOrden.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=item['cantidad']
                    )
                except Producto.DoesNotExist:
                    # Aquí puedes decidir qué hacer si un producto no existe
                    # Por ejemplo, saltar ese item o devolver un error
                    continue  # Ignora el producto y continúa con el siguiente

            return JsonResponse({'status': 'ok', 'orden_id': orden.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
@login_required
def actualizar_estado_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in dict(Orden.ESTADOS):
            orden.estado = nuevo_estado
            orden.save()
    # Redirige según rol
    rol = request.user.perfil.rol
    if rol == 'bodeguero':
        return redirect('bodeguero_inicio')
    elif rol == 'contador':
        return redirect('contador_inicio')
    else:
        return redirect('admin_inicio')