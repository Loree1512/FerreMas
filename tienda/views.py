from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Orden, ItemOrden, Perfil
from .forms import ProductoForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
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
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_inicio')  # Cambia por el nombre de tu URL
    else:
        form = ProductoForm()
    productos = Producto.objects.all()
    ordenes = Orden.objects.all()
    return render(request, 'tienda/admin_inicio.html', {
        'form': form,
        'productos': productos,
        'ordenes': ordenes,
    })
    
@require_POST
@login_required
def actualizar_estado_bodega(request, orden_id):
    if not request.user.perfil.rol == 'bodeguero':
        return redirect('inicio')

    orden = Orden.objects.get(id=orden_id)
    nuevo_estado = request.POST.get('estado')

    if nuevo_estado in dict(Orden.ESTADOS):
        orden.estado = nuevo_estado
        orden.save()

    return redirect('bodeguero_inicio')


@login_required
def bodeguero_inicio(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'bodeguero':
        return redirect('inicio')

    ordenes = Orden.objects.filter(estado__in=[
        'aceptado_por_vendedor',
        'preparando',
        'entregado_a_vendedor'
    ]).order_by('-fecha')

    return render(request, 'tienda/bodeguero/inicio.html', {'ordenes': ordenes})

@require_POST
@login_required
def limpiar_historial_bodeguero(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'bodeguero':
        return redirect('inicio')

    Orden.objects.filter(estado='entregado_a_vendedor').delete()
    messages.success(request, "Historial limpiado correctamente.")
    return redirect('bodeguero_inicio')

def contador_inicio(request):
    ordenes = Orden.objects.filter(
        metodo_pago='paypal',
        estado__in=['entregado_a_cliente', 'validado', 'completado']  # estados en los que quieres que aparezca
    )
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

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password)

        # Crear o actualizar perfil con rol cliente
        perfil, created = Perfil.objects.get_or_create(user=user)
        if not created:
            perfil.rol = 'cliente'
            perfil.save()
        else:
            perfil.rol = 'cliente'
            perfil.save()

        messages.success(request, 'Usuario registrado correctamente.')
        return redirect('inicio')

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
            perfil = getattr(user, 'perfil', None)
            if perfil:
                if perfil.rol == 'bodeguero':
                    return redirect('bodeguero_inicio')
                elif perfil.rol == 'contador':
                    return redirect('contador_inicio')
            if user.is_staff or user.is_superuser:
                return redirect('admin_inicio')  # Vendedor u otro staff
            else:
                return redirect('inicio')  # Usuario común
        else:
            return render(request, 'tienda/login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'tienda/login.html')

def productos_por_categoria(request, categoria):
    productos = Producto.objects.filter(categoria=categoria)
    nombre_categoria = dict(Producto.CATEGORIAS).get(categoria, categoria.title())
    return render(request, 'tienda/productos_categoria.html', {
        'productos': productos,
        'nombre_categoria': nombre_categoria,
    })

def formulario_cliente(request):
    return render(request, 'tienda/formulario_cliente.html')
@csrf_exempt

#REGISTRO ORDEN COMPRA

def registrar_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            direccion = data.get('direccion')
            sucursal = data.get('sucursal')
            carrito = data.get('carrito', [])
            total = data.get('total')
            nombre = data.get('nombre')
            email = data.get('email')
            paypal_payment_id = data.get('paypal_payment_id')  # nuevo campo
            fecha_pago = data.get('fecha_pago')  # opcional, si lo envías como string datetime

            orden = Orden.objects.create(
                nombre_cliente=nombre,
                email=email,
                total=total,
                usuario=request.user if request.user.is_authenticated else None,
                paypal_payment_id=paypal_payment_id,  # guardar el id del pago
                metodo_pago='paypal',  # marca que es pago PayPal
                estado='pendiente',    # estado inicial, o el que uses
            )

            # Si quieres guardar la fecha de pago y la recibes como string,
            # deberías convertirla a datetime, ejemplo:
            if fecha_pago:
                from django.utils.dateparse import parse_datetime
                orden.fecha_pago = parse_datetime(fecha_pago)
                orden.save()

            for item in carrito:
                try:
                    producto = Producto.objects.get(id=item['id'])
                    cantidad = item['cantidad']
                    ItemOrden.objects.create(
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad
                    )
                    if producto.stock >= cantidad:
                        producto.stock -= cantidad
                        producto.save()
                    else:
                        return JsonResponse({'error': f'No hay suficiente stock para {producto.nombre}'},status=400)
                except Producto.DoesNotExist:
                    continue

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

        # Si el bodeguero quiere marcar como entregado, lo completamos
        if nuevo_estado == 'entregado_a_vendedor':
            orden.estado = 'completado'
        elif nuevo_estado in dict(Orden.ESTADOS):
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



@login_required
def procesar_orden(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)

    # Solo el vendedor puede aceptar o rechazar
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'vendedor':
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('inicio')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aceptar':
            orden.estado = 'aceptado_por_vendedor'
            orden.aceptado_por_vendedor = True
            orden.save()
            messages.success(request, 'Pedido aceptado y enviado al bodeguero.')
        elif accion == 'rechazar':
            orden.estado = 'rechazada'
            orden.save()
            messages.info(request, 'Pedido rechazado.')

    return redirect('admin_inicio')  # o admin_ordenes, según tu lógica

def redirect_panel_por_rol(user):
    perfil = getattr(user, 'perfil', None)
    if perfil:
        if perfil.rol == 'vendedor':
            return redirect('admin_inicio')      # Panel vendedor
        elif perfil.rol == 'bodeguero':
            return redirect('bodeguero_inicio')  # Panel bodeguero
        elif perfil.rol == 'contador':
            return redirect('contador_inicio')
    # Por defecto
    return redirect('inicio')

@csrf_exempt
@login_required
def actualizar_estado_contador(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    if request.method == 'POST' and request.user.perfil.rol == 'contador':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in dict(Orden.ESTADOS):
            orden.estado = nuevo_estado
            orden.save()
    return redirect('contador_inicio')


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('admin_inicio') 

def admin_ordenes_view(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        ordenes = Orden.objects.all()
        return render(request, 'tienda/admin_ordenes.html', {'ordenes': ordenes})
    else:
        return redirect('login')

def buscar_productos(request):
    query = request.GET.get('q', '')
    resultados = Producto.objects.filter(nombre__icontains=query) if query else []
    return render(request, 'tienda/busqueda.html', {'resultados': resultados, 'query': query})

def ordenes_bodeguero(request):
    ordenes = Orden.objects.filter(estado__in=['pendiente', 'preparando', 'completado']).order_by('-fecha')
    return render(request, 'tienda/bodeguero_ordenes.html', {'ordenes': ordenes})

def bodeguero_productos(request):
    # Mostrar productos existentes
    productos = Producto.objects.all().order_by('-id')
    # Formulario para agregar producto
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Puedes agregar un mensaje de éxito aquí
    else:
        form = ProductoForm()
    return render(request, 'tienda/bodeguero_productos.html', {
        'form': form,
        'productos': productos
    })

@user_passes_test(lambda u: u.is_superuser)
def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            form.cleaned_data['grupos'].set(user.groups)
            user.groups.set(form.cleaned_data['grupos'])
            return redirect('admin_inicio')
    else:
        form = CrearUsuarioForm()
    return render(request, 'tienda/admin_usuarios.html', {'form': form})


def actualizar_stock(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        nuevo_stock = request.POST.get('stock')
        try:
            nuevo_stock = int(nuevo_stock)
            if nuevo_stock >= 0:
                producto.stock = nuevo_stock
                producto.save()
                messages.success(request, f'Stock actualizado a {nuevo_stock} para "{producto.nombre}".')
            else:
                messages.error(request, 'El stock debe ser un número positivo.')
        except ValueError:
            messages.error(request, 'Stock inválido.')

    return redirect('admin_inicio')

def actualizar_disponible(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        nuevo_valor = request.POST.get('disponible') == 'True'

        if producto.stock == 0 and nuevo_valor:
            messages.error(request, 'No puedes marcar como disponible un producto con stock 0.')
        else:
            producto.disponible = nuevo_valor
            producto.save()
            estado = "disponible" if nuevo_valor else "no disponible"
            messages.success(request, f'Producto "{producto.nombre}" ahora está {estado}.')
    return redirect('admin_inicio')

@login_required
def actualizar_estado_bodega(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)

    # Validación de rol bodeguero
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'bodeguero':
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('inicio')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'preparando' and orden.estado == 'aceptado_por_vendedor':
            orden.estado = 'preparando'
            orden.save()
            messages.success(request, 'La orden ha sido marcada como "En preparación".')

        elif accion == 'entregado' and orden.estado == 'preparando':
            orden.estado = 'entregado_a_vendedor'
            orden.save()
            messages.success(request, 'La orden ha sido marcada como "Entregada a vendedor".')

        else:
            messages.warning(request, 'Acción inválida para el estado actual.')

    return redirect('bodeguero_inicio')

@login_required
def actualizar_estado_vendedor(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)

    # Validación de rol vendedor
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'vendedor':
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('inicio')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'entregado_cliente' and orden.estado == 'entregado_a_vendedor':
            orden.estado = 'entregado_a_cliente'
            orden.save()
            messages.success(request, 'La orden ha sido marcada como "Entregada al cliente".')
        else:
            messages.warning(request, 'Acción no permitida en el estado actual.')

    return redirect('admin_ordenes')  # O a la vista de vendedor

@login_required
def verificar_pago(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    if request.method == 'POST':
        orden.verificado_por_contador = True
        orden.save()
        messages.success(request, 'Pago verificado correctamente.')
    return redirect('contador_inicio')

def actualizar_estado_contador(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)

    if request.method == 'POST':
        orden.verificado_por_contador = True
        # Opcional: Cambiar estado a 'validado' si quieres reflejarlo también
        orden.estado = 'validado'
        orden.save()
        messages.success(request, f'Pago de la orden #{orden.id} marcado como verificado.')

    return redirect('contador_inicio')

def limpiar_historial_vendedor(request):
    if request.method == "POST":
        Orden.objects.filter(usuario=request.user).update(ocultar_para_vendedor=True)
        messages.success(request, "Historial limpiado correctamente.")
    return redirect('admin_ordenes')

# Vista para limpiar historial del contador (por ejemplo borrar órdenes verificadas)
def limpiar_historial_contador(request):
    Orden.objects.filter(verificado_por_contador=True).delete()
    messages.success(request, "Historial de pagos verificados eliminado correctamente.")
    return redirect('contador_inicio')

