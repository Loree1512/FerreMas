from django.db import models

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
