from django.contrib import admin
from parking.models import Aparcamientos, ContactosParking, Comentarios, ParkingSeleccion, PaginaPersonal,EstiloUser

# Register your models here.
admin.site.register([Aparcamientos, ContactosParking, Comentarios, ParkingSeleccion, PaginaPersonal, EstiloUser])
