from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Aparcamientos (models.Model):
    nombre = models.CharField(max_length=70)
    descripcion = models.TextField()
    urlP = models.URLField(max_length=200)
    Accesibilidad = models.BooleanField()
    direccion = models.CharField(max_length=60)
    barrio = models.CharField(max_length=20)
    distrito = models.CharField(max_length=20)
    latitud = models.FloatField()
    longitud = models.FloatField()
    nComen = models.IntegerField()

class ContactosParking (models.Model):
    Aparcamiento = models.ForeignKey(Aparcamientos)
    telefono = models.IntegerField()
    email = models.CharField(max_length=32)

class Comentarios (models.Model):
    Aparcamiento = models.ForeignKey(Aparcamientos)
    Comentario = models.TextField()

class PaginaPersonal (models.Model):
    Titulo = models.CharField(max_length=32)
    usuario = models.OneToOneField(User)

class ParkingSeleccion (models.Model):
    Aparcamiento = models.ForeignKey(Aparcamientos)
    Usuario = models.ForeignKey(User)
    FichaPersonal = models.ForeignKey(PaginaPersonal)
    Fecha = models.DateField(auto_now=True)
