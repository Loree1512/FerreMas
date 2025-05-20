from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROL_CHOICES = [
        ('vendedor', 'Vendedor'),
        ('bodeguero', 'Bodeguero'),
        ('contador', 'Contador'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    def __str__(self):
        return f'{self.user.username} - {self.rol}'

class Producto(models.Model):
    CATEGORIAS = [
        ('manuales', 'Herramientas manuales'),
        ('materiales', 'Materiales'),
        ('electronica', 'Electricidad'),
        ('plomeria', 'Plomería'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    def __str__(self):
        return self.nombre

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_cliente = models.CharField(max_length=100)
    email = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('preparando', 'Preparando'),
        ('entregado_a_vendedor', 'Entregado a vendedor'),
        ('entregado_a_cliente', 'Entregado a cliente'),
    ]
    estado = models.CharField(max_length=30, choices=ESTADOS, default='pendiente')

    metodo_pago = models.CharField(max_length=30, default='paypal')  # o 'transferencia'

    def __str__(self):
        return f'Orden #{self.id} - {self.nombre_cliente}'
    
class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

    def __str__(self):
        return f'{self.producto.nombre} x {self.cantidad}'