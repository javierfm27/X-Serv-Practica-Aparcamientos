from django.shortcuts import render
from django.template import Template, Context
from django.template.loader import get_template
from django.http import HttpResponse,HttpResponseNotFound
from parking.models import *
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import logout, authenticate, login
from django.db import models
from urllib.parse import unquote_plus

enlaceInicio = "<a href='/'> Inicio </a>"
enlaceTodos = "<a href='/aparcamientos'>Todos</a>"
enlaceAyuda = "<a href='/about'>Ayuda</a>"

"""
RELLENAR FOOTER
"""
def footer():
    footerHtml = "Esta aplicacion utiliza datos del portal de datos abiertos de la ciudad de Madrid" \
            + "<a href=''> XML de Datos</a>" \
            + "<a href=''> Descripcion De Contenido XML</a> @2017"

def stringLogin(request): #Devuelve el string de Login, Logout.
    logeado = False
    if request.user.is_authenticated():
        header = "Usuario: " + str(request.user) + ". " + "<a href='/logout'>Logout</a>"
        logeado = True
    else:
        header = "<form action='/login' method='POST'>"\
            + "Usuario: <input type='text' name='usuario'><br>" \
            + "Contraseña: <input type='password' name='contraseña'><br> "\
            + "<input type='submit' value='Enviar'></form>"
    return header, logeado


def listaAparcamientos(lista, nombreLista, request, flag):
    #Lista de Aparcamientos, flag para distinguir cuando le paso un aparcamiento o una lista de estos
    Content = nombreLista
    if flag == 0:
        for p in lista:
            if request.user.is_authenticated():
                botonAñadir = "<form action='/" + str(request.user) + "' method='POST'>" \
                        + "<button type='submit' name='Add' value='" + str(p.id) + "'> Add </button></form>"
                Content = Content + "<a href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<a href='/aparcamientos/" + str(p.id) + "'> Mas Info</a><br>"+ botonAñadir + "<br>"
            else:
                Content = Content + "<a href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<a href='/aparcamientos/" + str(p.id) + "'> Mas Info</a><br>"
        return Content
    else:
        if request.user.is_authenticated():
            botonAñadir = "<form action='/" + str(request.user) + "' method='POST'>" \
                    + "<button type='submit' name='Add' value='" + str(lista.id) + "'> Add </button></form>"
            Content = Content + "<a href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>"+ botonAñadir + "<br>"
        else:
            Content = Content + "<a href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>"
        return Content

def listaPaginasPersonalesBarra():
    #Enlaces a Paginas Personales, Pagina Principal
    ContentLateral = "<h3>Paginas Personales</h3>"
    listaUsuarios = User.objects.all()
    for u in listaUsuarios:
        try:
            titulo = PaginaPersonal.objects.get(usuario=u.id).Titulo
            if titulo == "":
                ContentLateral = ContentLateral + "<a href='/" + u.username + "'> Pagina de " + u.username + "</a> - " + u.username + "<br>"
            else:
                ContentLateral =  ContentLateral + "<a href='/" + u.username + "'>" + titulo + "</a> - " + u.username + "<br>"
        except PaginaPersonal.DoesNotExist:
            ContentLateral = ContentLateral + "<a href='/" + u.username + "'> Pagina de " + u.username + "</a> - " + u.username + "<br>"
    return (ContentLateral)


def postUsuario(request):
    #Procesa el POST que haremos sobre /(usuario)
    keyPost, valuePost = request.body.decode('utf-8').split("=")
    print(valuePost)
    #Antes de nada comprobaremos si existe la pagina, si no, la creamos
    usuario = User.objects.get(username=str(request.user))
    try:
        PaginaPersonal.objects.get(usuario=usuario)
    except PaginaPersonal.DoesNotExist:
        nuevaPagina = PaginaPersonal(Titulo="", usuario=usuario)
        nuevaPagina.save()
    #Comprobamos si se esta haciendo un POST para añadir aparcamiento o para modificar el titulo de nuestra coleccion
    if keyPost == 'Add':
        coleccion = PaginaPersonal.objects.get(usuario=usuario)
        parking = Aparcamientos.objects.get(id=int(valuePost))
        adiccion = ParkingSeleccion(Aparcamiento=parking, Usuario=usuario, FichaPersonal=coleccion)
        adiccion.save()
    elif keyPost == 'Titulo':
        pagina = PaginaPersonal.objects.get(usuario=usuario)
        pagina.Titulo = unquote_plus(valuePost)
        pagina.save()

def obtainBodyUser(usuarioGET, request):
    #Funcion que genera el Html para /usuario

    #Comprobamos que dicha coleccion exista, si no, la creamos y por tanto no tendra parkings
    try:
        coleccion = PaginaPersonal.objects.get(usuario=usuarioGET)
        #Como existe. Comprobamos si el usuario de la peticion es el mismo de la pagina
        if coleccion.Titulo == "":
            Titulo = "Pagina de " + str(usuarioGET)
        else:
            Titulo = coleccion.Titulo
        if str(request.user) == str(usuarioGET):
            headerBody = "<h2>" + Titulo + "</h2><br>" \
                + "<form action='/" + str(request.user) + "' method='POST'>" \
                + "Introduce un titulo para la pagina: <input type='text' name='Titulo'>" \
                + "<input type='submit' value='Enviar'></form>"
        else:
            headerBody = "<h2>" + Titulo + "</h2><br>"

        #Obtenemos la lista de Aparcamientos seleccionados
        listaParkings = ParkingSeleccion.objects.filter(FichaPersonal=coleccion)
        ContentBody = ""
        for i in listaParkings:
            aparcamiento = i.Aparcamiento
            ContentBody = ContentBody + listaAparcamientos(aparcamiento, "", request, 1)
        return(headerBody, ContentBody)
    except PaginaPersonal.DoesNotExist:
        nuevaPagina = PaginaPersonal(Titulo="", usuario=usuarioGET)
        nuevaPagina.save()
        return (nuevaPagina.Titulo, "No hay ningun Parking en esta coleccion. De momento")

#################################################################################################################################3
# Create your views here.
@csrf_exempt
def barra(request):
    header, booleanLogin = stringLogin(request)
    if request.method == 'GET':
        boton = "<form method='POST'>"\
            + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
        Content = "<h2>Aparcamientos Mas Comentados</h2>" + boton
        #Aparcamientos mas comentados
        parkings = Aparcamientos.objects.all()
        aparcamientos = parkings.order_by('nComen')
        Content = listaAparcamientos(aparcamientos, Content, request, 0)

    elif request.method == 'POST':
        opcionAccesibles = request.body.decode('utf-8')
        opcionAccesibles = opcionAccesibles.split("=")[1]

        if (int(opcionAccesibles) == 1):
            boton = "<form method='POST'>" \
                + "<button type='submit' name='Accesibilidad' value=0> Mostrar Todos</button><form><br><br>"
            Content = "<h2>Aparcamientos Accesibles</h2>" + boton
            #Aparcamientos Accesibles
            parkings = Aparcamientos.objects.filter(Accesibilidad=True)
            parkings = parkings.order_by('nComen')
            Content = listaAparcamientos(parkings, Content, request, 0)

        else:
            boton = "<form method='POST'>"\
                + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
            Content = "<h2>Aparcamientos Mas Comentados</h2>" + boton
            #Aparcamientos mas comentados
            parkings = Aparcamientos.objects.all()
            aparcamientos = parkings.order_by('nComen')
            Content = listaAparcamientos(aparcamientos, Content, request, 0)

    #Paginas Personales
    ContentLateral = listaPaginasPersonalesBarra()
    return HttpResponse(header + enlaceTodos + Content + ContentLateral)



@csrf_exempt
def seleccionPersonal(request, nombreUser):
    header, login = stringLogin(request)
    if request.method == 'GET':
        try:
            usuario = User.objects.get(username=str(nombreUser))
            titulo, Content = obtainBodyUser(usuario,request)
        except User.DoesNotExist:
            return HttpResponseNotFound("No Existe El Usuario")
    elif request.method == 'POST':
        postUsuario(request)
        return redirect(seleccionPersonal,str(request.user))
    return HttpResponse(header + titulo + Content)

@csrf_exempt
def todosAparcamientos(request):
    #Funcion que mostrara la lista de Parkings

    header, login = stringLogin(request)
    formularioFiltrado = "<form method='POST'>"\
        + "Buscar por Distrito: <input type='text' name='Distrito'>" \
        + "<input type='submit' value='Filtrar'></form>"
    #Si no hay Parkings en la base de datos, los obtendremos mediante el XML
    try:
        if request.method == 'GET':
            parkings = Aparcamientos.objects.all()
            ContentBody = "<ul><h2> Listado De Parkings</h2>"
            for i in parkings:
                ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a></li>"
            ContentBody = ContentBody + "</li>"
        elif request.method == 'POST':
            ContentBody = "Probando"
            Distrito = request.body.decode('utf-8').split("=")[1]
            Distrito = unquote_plus(Distrito)
            parkings = Aparcamientos.objects.filter(distrito=Distrito)
            ContentBody = "<ul><h2> Listado De Parkings</h2>"
            for i in parkings:
                ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a></li>"
            ContentBody = ContentBody + "</li>"
        return HttpResponse(header + formularioFiltrado + ContentBody)
    except Aparcamientos.DoesNotExist:
        return HttpResponse("Aqui Usaremos el XML y obtendremos los datos")

def infoAparcamiento(request, id):
    return HttpResponse("AQUI MOSTRAREMOS MUCHA INFOR")

@csrf_exempt
def loginUser(request):
    usuario = request.POST['usuario']
    contraseña = request.POST['contraseña']
    user = authenticate(username=usuario, password=contraseña)
    if user is not None:
        login(request, user)
        return redirect(barra)
    else:
        return HttpResponse("No es valido el Usuario." + enlaceInicio)


def mylogout(request):
    logout(request)
    return redirect(barra)
