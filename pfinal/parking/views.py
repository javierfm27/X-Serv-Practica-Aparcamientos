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

def stringLogin(request): #Devuelve el string de Login, Logout.
    logeado = False
    if request.user.is_authenticated():
        header = "<span class='.t-center'> Usuario: " + str(request.user) + ". " + "<a href='/logout'>Logout</a></span>"
        logeado = True
    else:
        header = "<form class='.t-left' action='/login' method='POST'>"\
            + "Usuario:<br><input type='text' name='usuario'><br>" \
            + "Contraseña:<br><input type='password' name='contraseña'><br> "\
            + "<input type='submit' value='Enviar'></form>"
    return header, logeado


def listaAparcamientos(lista, request, flag):
    #Lista de Aparcamientos, flag para distinguir cuando le paso un aparcamiento o una lista de estos
    Content = []
    if flag == 0:
        for p in lista:
            if request.user.is_authenticated():
                botonAñadir = "<form action='/" + str(request.user) + "' method='POST'>" \
                        + "<button type='submit' name='Add' value='" + str(p.id) + "'> Add </button></form>"
                Content.append("<a href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<a href='/aparcamientos/" + str(p.id) + "'> Mas Info</a><br>"+ botonAñadir + "<br>")
            else:
                Content.append("<a href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<a href='/aparcamientos/" + str(p.id) + "'> Mas Info</a><br>")
        return Content
    else:
        seleccion = ParkingSeleccion.objects.get(Aparcamiento=lista)
        if request.user.is_authenticated():
            botonAñadir = "<form action='/" + str(request.user) + "' method='POST'>" \
                    + "<button type='submit' name='Add' value='" + str(lista.id) + "'> Add </button></form>"
            Content.append("<a href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>" \
                + "Fecha Seleccion: " + str(seleccion.Fecha) + "<br>" + botonAñadir + "<br>")
        else:
            Content.append("<a href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>" \
                + "Fecha Seleccion: " + str(seleccion.Fecha))
        return Content

def listaPaginasPersonalesBarra():
    #Enlaces a Paginas Personales, Pagina Principal
    ContentLateral = []
    listaUsuarios = User.objects.all()
    for u in listaUsuarios:
        try:
            titulo = PaginaPersonal.objects.get(usuario=u.id).Titulo
            if titulo == "":
                ContentLateral.append("<a href='/" + u.username + "'> Pagina de " + u.username + "</a>Usuario: " + u.username)
            else:
                ContentLateral.append("<a href='/" + u.username + "'>" + titulo + "</a>Usuario: " + u.username)
        except PaginaPersonal.DoesNotExist:
            ContentLateral.append("<a href='/" + u.username + "'> Pagina de " + u.username + "</a>Usuario: " + u.username)
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
        añadir = True
        listaParkings = ParkingSeleccion.objects.filter(Usuario=usuario)
        for i in listaParkings:
            if i.Aparcamiento.nombre == parking.nombre:
                añadir = False
                break
        if añadir == True:
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

def obtainInfoParking(aparcamiento):
    try:
        contacto = ContactosParking.objects.get(Aparcamiento=aparcamiento)
        htmlContacto = "<dt>Tlfno. Contacto</dt><dd>"+ contacto.telefono + "</dd><dt>Email Contacto</dt><dd>"+ contacto.email + "</dd>"
    except ContactosParking.DoesNotExist:
        htmlContacto = "<dt>Contacto</dt><dd> No hay Contacto</dd>"
    #Body HTML
    bodyHtml = "<h3>Info Detallada</h3>" \
            + "<dl><dt>Nombre de Parking</dt>" \
                + "<dd>" + aparcamiento.nombre + "</dd>" \
                + "<dt>Direccion</dt>" \
                + "<dd>" + aparcamiento.direccion + "</dd>" \
                + "<dt>Accesibilidad</dt>" \
                + "<dd>" + str(aparcamiento.Accesibilidad) + "</dd>" \
                + "<dt>Latitud y Longitud</dt>" \
                + "<dd>" + str(aparcamiento.latitud) + str(aparcamiento.longitud) + "</dd>" \
                + "<dt>Barrio</dt>" \
                + "<dd>" + aparcamiento.barrio + "</dd>" \
                + "<dt>Distrito</dt>" \
                + "<dd>" + aparcamiento.distrito + "</dd>" \
                + "<dt>Descripcion</dt>" \
                + "<dd>" + aparcamiento.descripcion + "</dd>" \
                + htmlContacto + "</dl>"
    try:
        listaComentarios = Comentarios.objects.filter(Aparcamiento=aparcamiento)
        htmlComentarios = "Comentarios<br><ul>"
        for i in listaComentarios:
            htmlComentarios = htmlComentarios + "<li>" + i.Comentario + "</li></ul>"
    except Comentarios.DoesNotExist:
        htmlComentarios = "No Hay Comentarios para este aparcamiento"
    return (bodyHtml + htmlComentarios)

#################################################################################################################################3
# Create your views here.
@csrf_exempt
def barra(request):
    header, booleanLogin = stringLogin(request)
    if request.method == 'GET':
        boton = "<form method='POST'>"\
            + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
        TituloBarra = "Aparcamientos Mas Comentados"
        #Aparcamientos mas comentados
        parkings = Aparcamientos.objects.all()
        aparcamientos = parkings.order_by('-nComen')
        Content = listaAparcamientos(aparcamientos, request, 0)

    elif request.method == 'POST':
        opcionAccesibles = request.body.decode('utf-8')
        opcionAccesibles = opcionAccesibles.split("=")[1]

        if (int(opcionAccesibles) == 1):
            boton = "<form method='POST'>" \
                + "<button type='submit' name='Accesibilidad' value=0> Mostrar Todos</button><form><br><br>"
            TituloBarra = "Aparcamientos Accesibles"
            #Aparcamientos Accesibles
            parkings = Aparcamientos.objects.filter(Accesibilidad=True)
            parkings = parkings.order_by('nComen')
            Content = listaAparcamientos(parkings, request, 0)

        else:
            boton = "<form method='POST'>"\
                + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
            TituloBarra = "<h2>Aparcamientos Mas Comentados</h2>"
            #Aparcamientos mas comentados
            parkings = Aparcamientos.objects.all()
            aparcamientos = parkings.order_by('nComen')
            Content = listaAparcamientos(aparcamientos,request, 0)

    #Paginas Personales
    ContentLateral = listaPaginasPersonalesBarra()
    #Una vez obtenido el contenido vamos a renderizar la plantilla
        #Los enlaces que tendra la pagina principal son: Todos, Ayuda
    enlaces = []
    enlaces.append(enlaceTodos)
    enlaces.append(enlaceAyuda)
    #Renderizamos
    plantilla = get_template("barra.html")
    Contexto = ({'login': header,
                'enlaces': enlaces,
                'boton': boton,
                'TituloBarra': TituloBarra,
                'Aparcamientos': Content,
                'Paginas': ContentLateral})
    return HttpResponse(plantilla.render(Contexto))



@csrf_exempt
def seleccionPersonal(request, nombreUser):
    header, login = stringLogin(request)
    #Definimos la barra de enlaces(para utilizarla en el caso de Error)
    enlaces = []
    enlaces.append(enlaceInicio)
    enlaces.append(enlaceTodos)
    enlaces.append(enlaceAyuda)

    
    #Controlamos el POST y el get
    if request.method == 'GET':
        try:
            usuario = User.objects.get(username=str(nombreUser))
            titulo, Content = obtainBodyUser(usuario,request)
        except User.DoesNotExist:
            plantilla = get_template('error.html')
            contenidoNotFound = "NO EXISTE EL USUARIO " + str(nombreUser)
            Content = ({'login': header,
                        'enlaces': enlaces,
                        'Contenido': contenidoNotFound})
            return HttpResponseNotFound(plantilla.render(Content))
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

@csrf_exempt
def infoAparcamiento(request, id):
    #Definimos la barra de enlaces(para utilizarla en el caso de Error)
    enlaces = []
    enlaces.append(enlaceInicio)
    enlaces.append(enlaceTodos)
    enlaces.append(enlaceAyuda)
    header, login = stringLogin(request)

    #Solicitamos la informacion del Parking solitcitado
    if request.method == 'GET':
        if login:
            formularioComentario = "<form method='POST'>" \
                + "Introduce un Comentario<br><input type='text' id='Comentarios'  size=32 name='Comentario'>" \
                + "<input type='submit' value='Enviar'>"
        else:
            formularioComentario = ""
        try:
            parking = Aparcamientos.objects.get(id=id)
            bodyHtml = obtainInfoParking(parking)
            Content = bodyHtml + formularioComentario
            return HttpResponse(Content)
        except Aparcamientos.DoesNotExist:
            plantilla = get_template("error.html")
            ContentInfo = "No existe el aparcamiento solicitado"
            Content = ({'login': header,
                        'enlaces': enlaces,
                        'Contenido': ContentInfo})
            return HttpResponseNotFound(plantilla.render(Content))

    #Aqui controlamos el postear un comentario
    elif request.method == 'POST':
        comentarioPOST = request.body.decode('utf-8').split("=")[1]
        comentarioPOST = unquote_plus(comentarioPOST)
        #1ºAñadimos al modelo Comentarios
        aparcamiento = Aparcamientos.objects.get(id=id)
        comentarioNuevo = Comentarios(Aparcamiento=aparcamiento, Comentario=comentarioPOST)
        comentarioNuevo.save()
        #2ºAhora lo que haremos sera sumar uno al contador de Comentarios, para luego en la pagina principal ordenar de mayor a  menor
        aparcamiento.nComen = aparcamiento.nComen + 1
        aparcamiento.save()
        return redirect(infoAparcamiento,aparcamiento.id)


def informacion(request):
    #Definimos la barra de enlaces(para utilizarla en el caso de Error)
    enlaces = []
    enlaces.append(enlaceInicio)
    enlaces.append(enlaceTodos)
    enlaces.append(enlaceAyuda)

    header, login = stringLogin(request)

    Contenido = "<p>Aplicacion Web que aglutina informacion sobre aparcamientos en la ciudad de Madrid<p>"\
        + "<p>La aplicacion consistira en comentar los aparcamientos disponibles de Madrid, dando al usuario" \
        + "la interfaz de crear una pagina con sus Parkings Favoritos de Madrid, donde la app recogera, "\
        + "el nombre del Parking, descripcion, localizacion, telefono y email de contacto, etc.</p>" \
        + "<p> Ademas se podran comentar sobre los aparcamientos, dando asi al usuario informacion sobre experiencias"\
        + "recogidas de tal aparcamiento por otros usuarios</p>"\
        + "<p>Aplicacion diseñada por Javier Fernandez Morata<br> Alumno de ETSIT del grado de Tecnologías</p>"
    plantilla = get_template("error.html")
    Content = ({'Contenido': Contenido,
                'login': header,
                'enlaces': enlaces})
    return HttpResponse(plantilla.render(Content))

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
