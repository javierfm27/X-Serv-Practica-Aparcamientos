"""pfinal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from parking import views
from pfinal import settings
from django.views.static import *
import os

urlpatterns = [
    url(r'^static/(?P<path>.*)$',serve,{'document_root':settings.STATIC_URL}),
    url(r'^main.css', views.estiloPropio,name='Pagina donde renderizo el CSS dinamico'),
    url(r'^personal.css',views.estiloPropio),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.barra, name="Pagina Principal del sitio"),
    url(r'^recarga', views.obtengoDatos, name="Obtengo los datos y redirigo a la pagina principal"),
    url(r'^login', views.loginUser, name="Pagina que logea con los datos obtenidos del formulario Usuario y Contraseña"),
    url(r'^logout', views.mylogout, name="Pagina para desconectar"),
    url(r'^aparcamientos/(\d+)', views.infoAparcamiento, name="Muestra todos los datos de un Parking"),
    url(r'^about$', views.informacion, name="Pagina que explica la funcionalidad de la practica"),
    url(r'^aparcamientos$', views.todosAparcamientos, name="Listado de todos los Parkings que maneja la App"),
    url(r'^(.+)/xml$', views.showXml, name='Pagina donde mostraremos el xml del usuario en cuestion '),
    url(r'^(.+)',views.seleccionPersonal, name="Paginas de los usuarios registrados"),
]
