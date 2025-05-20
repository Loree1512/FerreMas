from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return f'Orden #{self.id} - {self.nombre_cliente}'
    
class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

    def __str__(self):
        return f'{self.producto.nombre} x {self.cantidad}'