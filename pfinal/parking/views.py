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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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


def listaAparcamientos(lista, request, flag, usuario):
    #Lista de Aparcamientos, flag para distinguir cuando le paso un aparcamiento o una lista de estos
    if flag == 0:
        Content = []
        for p in lista:
            if request.user.is_authenticated():
                botonAñadir = "<form action='/" + str(request.user) + "' method='POST'>" \
                        + "<button type='submit' name='Add' value='" + str(p.id) + "'> Add </button></form>"
                Content.append("<p id='listado'><a class='info' href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<a class='info' href='/aparcamientos/" + str(p.id) + "'> Mas Info</a><br></p>"+ botonAñadir + "<br>")
            else:
                Content.append("<p id='listado'><a class='info' href='" + p.urlP + "'> " + p.nombre + "</a><br>" \
                    + "Direccion: " + p.direccion + "<br>" \
                    + "<span class='info'><a class='info' href='/aparcamientos/" + str(p.id) + "'> Mas Info</a></span></p><br>")
        return Content
    else:
        seleccion = ParkingSeleccion.objects.get(Aparcamiento=lista,Usuario=usuario)
        if request.user.is_authenticated():
            botonAñadir = "<form class='Personal' action='/" + str(request.user) + "' method='POST'>" \
                    + "<button type='submit' name='Add' value='" + str(lista.id) + "'> Add </button></form>"
            Content = "<a class='info' href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a class='info' href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>" \
                + "<span class='info'><span class='date'> Fecha Seleccion: " + str(seleccion.Fecha) + "</span></span><br>" + botonAñadir + "<br>"
        else:
            Content = "<a class='info' href='" + lista.urlP + "'> " + lista.nombre + "</a><br>" \
                + "Direccion: " + lista.direccion + "<br>" \
                + "<a class='info' href='/aparcamientos/" + str(lista.id) + "'> Mas Info</a><br>" \
                + "<span class='info'><span class='date'> Fecha Seleccion: " + str(seleccion.Fecha) + "</span></span>"
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
    print("post" + request.body.decode('utf-8'))
    listaPOST = request.body.decode('utf-8').split("&")
    if len(listaPOST) == 1:
        keyPost, valuePost = request.body.decode('utf-8').split("=")
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
    else:
        #1º Controlamos el color
        valorColor = listaPOST[0].split("=")[1]
        #2º Controlamos el tamaño de la letra
        tamañoLetra = listaPOST[1].split("=")[1]
        if tamañoLetra == "":
            tamañoLetra = 2.8
        try:
            usuario = User.objects.get(username=request.user)
            nuevoCSS = EstiloUser.objects.get(Usuario=usuario)
            nuevoCSS.Color = valorColor
            nuevoCSS.Tamaño = float(tamañoLetra)
            nuevoCSS.save()
        except EstiloUser.DoesNotExist:
            usuario = User.objects.get(username=request.user)
            nuevoCSS = EstiloUser(Tamaño=tamañoLetra,Color=valorColor,Usuario=usuario)
            nuevoCSS.save()



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
            formulario =   "<form id='formularioTitulo' action='/" + str(request.user) + "' method='POST'>" \
                + "Introduce un nombre para tu Coleccion<br><input type='text' name='Titulo'>" \
                + "<input type='submit' value='Enviar'></form>"
        else:
            formulario = ""

        #Obtenemos la lista de Aparcamientos seleccionados
        listaParkings = ParkingSeleccion.objects.filter(FichaPersonal=coleccion)
        paginator = Paginator(listaParkings, 5) #Mostrara 5 aparcamientos de 5 en 5
        #Obtenemos la pagina de Contactos
        pagina = request.GET.get('page')
        try:
            parkings = paginator.page(pagina)
        except PageNotAnInteger:
            parkings = paginator.page(1)
        except:
            parkings = paginator.page(paginator.num_pages)

        ContentBody = []
        for i in parkings:
            aparcamiento = i.Aparcamiento
            ContentBody.append(listaAparcamientos(aparcamiento,request, 1, usuarioGET))
        return(Titulo, formulario,ContentBody,parkings)
    except PaginaPersonal.DoesNotExist:
        nuevaPagina = PaginaPersonal(Titulo="", usuario=usuarioGET)
        nuevaPagina.save()
        return (nuevaPagina.Titulo,"" , "No hay ningun Parking en esta coleccion. De momento")

def obtainInfoParking(aparcamiento):
    contacto = ContactosParking.objects.get(Aparcamiento=aparcamiento)
    if not contacto.telefono == "S/T" or contacto.email == "":
        htmlContacto = "<li><strong>Tlfno. Contacto</strong> "+ contacto.telefono + "</li>"+ "<li><strong>Email Contacto</strong> "+ contacto.email + "</li>"
    else:
        htmlContacto = "<li><strong>Contacto</strong> No hay Contacto</li>"
    #Body HTML
    bodyHtml = "<h2 class='info'><span class='cat'>INFO APARCAMIENTO</span></h2>" \
            + "<ul class='info'><li><strong>Nombre de Parking: </strong>" \
                +  aparcamiento.nombre + "</li>" \
                + "<li><strong>Direccion: </strong>" \
                + aparcamiento.direccion + "</li>" \
                + "<li><strong>Accesibilidad: </strong>" \
                + str(aparcamiento.Accesibilidad) + "</li>" \
                + "<li><strong>Latitud: </strong>"\
                + str(aparcamiento.latitud) + "</li>" \
                + "<li><strong>Longitud: </strong>" \
                + str(aparcamiento.longitud) + "</li>" \
                + "<li><strong>Barrio: </strong>" \
                + aparcamiento.barrio + "</li>" \
                + "<li><strong>Distrito: </strong>" \
                +  aparcamiento.distrito + "</li>" \
                + "<li><strong>Descripcion: </strong>" \
                + aparcamiento.descripcion + "</li>" \
                + htmlContacto + "</ul>"
    try:
        listaComentarios = Comentarios.objects.filter(Aparcamiento=aparcamiento)
        htmlComentarios = "<h4 id='comments'><span class='comments'>Comentarios</span></h4><ul>"
        for i in listaComentarios:
            htmlComentarios = htmlComentarios + "<li class='comments'>" + i.Comentario + "</li>"
        htmlComentarios = htmlComentarios + "</ul><br>"
    except Comentarios.DoesNotExist:
        htmlComentarios = "No Hay Comentarios para este aparcamiento"
    return (bodyHtml + htmlComentarios)

def addParking(datosDic):
    direccion = datosDic['CLASE-VIAL'] +  "  " + datosDic['NOMBRE-VIA']
    if int(datosDic['ACCESIBILIDAD']) == 0:
        accesible = False
    else:
        accesible = True
    aparcamiento = Aparcamientos(nombre=datosDic['NOMBRE'], descripcion=datosDic['DESCRIPCION'],
            urlP=datosDic['CONTENT-URL'], Accesibilidad=accesible, direccion=direccion, barrio=datosDic['BARRIO'],
            distrito=datosDic['DISTRITO'], latitud=float(datosDic['LATITUD']), longitud=float(datosDic['LONGITUD']),
            nComen=0)
    aparcamiento.save()
    #Controlamos el Contacto
    print("Telfono-> " + str(datosDic['TELEFONO']))
    print("EMAIL-> " + str(datosDic['EMAIL']))
    if  not datosDic['TELEFONO'] == None:
        if not datosDic['EMAIL'] == None:
            nuevoContacto = ContactosParking(Aparcamiento=aparcamiento,telefono=datosDic['TELEFONO'],email=datosDic['EMAIL'])
            nuevoContacto.save()
        else:
            nuevoContacto = ContactosParking(Aparcamiento=aparcamiento,telefono=datosDic['TELEFONO'])
            nuevoContacto.save()
    else:
        nuevoContacto = ContactosParking(Aparcamiento=aparcamiento)
        nuevoContacto.save()

#################################################################################################################################3
# Create your views here.
@csrf_exempt
def barra(request):
    header, booleanLogin = stringLogin(request)
    if request.method == 'GET':
        #Aparcamientos mas comentados
        parkings = Aparcamientos.objects.all()
        if len(parkings) == 0:
            botonRecarga = "<form action='recarga' method='GET'>" \
                    + "<button type='submit' name='Recargar'> Obtener Aparcamientos</button></form>"
            Content = "No hay aparcamientos en la base de datos. " + botonRecarga
            plantilla =  get_template('error.html')
            enlaces = []
            enlaces.append(enlaceInicio)
            enlaces.append(enlaceTodos)
            enlaces.append(enlaceAyuda)
            Context = {'login': header,
                       'enlaces': enlaces,
                       'Contenido': Content}
            return HttpResponse(plantilla.render(Context))
        else:
            boton = "<form method='POST'>"\
                + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
            TituloBarra = "Aparcamientos Mas Comentados"
            aparcamientosComen = Aparcamientos.objects.filter(nComen__gt=0)
            if(len(aparcamientosComen) == 0):
                TituloBarra = "<h2> No hay Aparcamientos Comentados</h2>"
                Content = ""
            else:
                aparcamientos = aparcamientosComen.order_by('-nComen')[:5]
                Content = listaAparcamientos(aparcamientos, request, 0, request.user)

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
            Content = listaAparcamientos(parkings, request, 0, request.user)

        else:
            boton = "<form method='POST'>"\
                + "<button type='submit' name='Accesibilidad' value=1 >Mostrar Accesibles</button></form>"
            TituloBarra = "<h2>Aparcamientos Mas Comentados</h2>"
            #Aparcamientos mas comentados
            parkings = Aparcamientos.objects.all()
            aparcamientosComen = Aparcamientos.objects.filter(nComen__gt=0)
            aparcamientos = aparcamientosComen.order_by('-nComen')[:5]
            Content = listaAparcamientos(aparcamientos,request, 0, request.user)

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
            usuario = User.objects.get(username=nombreUser)
            titulo,formulario ,Content ,parkings = obtainBodyUser(usuario,request)
            if request.user == usuario:
                formularioEstilo = "<form method='POST'>" \
                        + "<label for='Color'>Escoge un color    </label>" \
                        + "<input id='Color' type='color' name='color'>" \
                        + "<label for='Size'>  Escoge un tamaño de letra(mm)     </label>"\
                        + "<input id='Size' min='2' max='4' step='0.10' type='number' name='sizeWord'>" \
                        + "<input type='submit' value='Enviar'>" \
                        + "</form>"
            else:
                formularioEstilo = ""
        except User.DoesNotExist:
            plantilla = get_template('error.html')
            contenidoNotFound = "NO EXISTE EL USUARIO " + str(nombreUser)
            #Renderizamos para el error
            Content = ({'login': header,
                        'enlaces': enlaces,
                        'Contenido': contenidoNotFound})
            return HttpResponseNotFound(plantilla.render(Content))
    elif request.method == 'POST':
        postUsuario(request)
        return redirect(seleccionPersonal,str(request.user))

    #Renderizamos para el html personal, ya que este es distinto que el de la Pagina Principal
    plantilla = get_template('personal.html')
    Context = ({'login': header,
                'enlaces': enlaces,
                'TituloPagina': titulo,
                'seleccionUsuario': Content,
                'formulario': formulario,
                'usuario': nombreUser,
                'estilo': formularioEstilo,
                'parkings': parkings})
    return HttpResponse(plantilla.render(Context))



def showXml(request, usuarioGET):
    from lxml import etree as et

    #Creamos el elemento raiz de nuestro XML
    rootXML = et.Element('Coleccion')
    docXml = et.ElementTree(rootXML)

    #Empezamos a crear el documento
    infoColeccion = et.SubElement(rootXML, 'infoColeccion')
    infoColeccion.text = "Coleccion Personal del usuario " + str(usuarioGET)

    #Aqui añadiremos los parkings
    Usuario = User.objects.get(username=usuarioGET)
    parkingsUsuario = ParkingSeleccion.objects.filter(Usuario=Usuario)
    for i in parkingsUsuario:
        aparcamientoTag = et.SubElement(rootXML,'aparcamiento')
        aparcamiento = Aparcamientos.objects.get(id=i.Aparcamiento.id)
        #Generamos un diccionario de Atributos donde ira la informacion
        nombreP = et.SubElement(aparcamientoTag, 'nombre')
        nombreP.text = aparcamiento.nombre
        descripcionP = et.SubElement(aparcamientoTag, 'descripcion')
        descripcionP.text = aparcamiento.descripcion
        urlP = et.SubElement(aparcamientoTag,'link')
        urlP.text = aparcamiento.urlP
        localizacion = et.SubElement(aparcamientoTag, 'localizacion')
        localizacion.text = aparcamiento.direccion
        barrioTag = et.SubElement(aparcamientoTag,'barrio')
        barrioTag.text = aparcamiento.barrio
        #Añadimos el contacto
        try:
            contacto = ContactosParking.objects.get(Aparcamiento=aparcamiento.id)
            contactoTag = et.SubElement(aparcamientoTag,'contacto')
            contactoTag.text = "Tlfno. " + contacto.telefono + " email: " + contacto.email
        except ContactosParking.DoesNotExist:
            contactoTag = et.SubElement(aparcamientoTag,'contacto')
            contactoTag.text = "No existe Contacto Alguno"

    return HttpResponse(et.tostring(rootXML,pretty_print=True),content_type='text/xml')



@csrf_exempt
def todosAparcamientos(request):
    #Funcion que mostrara la lista de Parkings

    header, login = stringLogin(request)
    formularioFiltrado = "<form  id='buscarDistrito' method='POST'>"\
        + "Buscar por Distrito: <select name='Distrito'>" \
        + "<option value='TODOS'>Todos</option>" \
        + "<option value='CENTRO'>Centro</option>" \
        + "<option value='CHAMARTIN'>Chamartin</option>" \
        + "<option value='TETUAN'>Tetuan</option>" \
        + "<option value='MONCLOA-ARAVACA'>Moncloa - Aravaca </option>" \
        + "<option value='RETIRO'>Retiro</option>" \
        + "<option value='SALAMANCA'>Salamanca</option>" \
        + "<option value='MORATALAZ'>Moratalaz</option>" \
        + "<option value='CHAMBERI'>Chamberi</option>" \
        + "<option value='SAN BLAS-CANILLEJAS'>San Blas - Canillejas</option>" \
        + "<option value='CIUDAD LINEAL'>Ciudad lineal</option>" \
        + "<option value='FUENCARRAL-EL PARDO'>Fuencarral - El pardo </option>" \
        + "<option value='ARGANZUELA'>Arganzuela</option>" \
        + "<option value='VILLA DE VALLECAS'>Villa de Vallecas</option>" \
        + "<option value='LATINA'>Latina</option>" \
        + "<option value='HORTALEZA'>Hortaleza</option>" \
        + "<option value='PUENTE DE VALLECAS'>Puente de Vallecas</option>" \
        + "<option value='CARABANCHEL'>Carabanchel</option>" \
        + "<option value='VILLAVERDE'>Villaverde</option>" \
        + "<option value='BARAJAS'>Barajas</option>" \
        + "</select>" \
        + "<input type='submit' value='Filtrar'></form>"
    enlaces = []
    enlaces.append(enlaceInicio)
    enlaces.append(enlaceTodos)
    enlaces.append(enlaceAyuda)
    #Si no hay Parkings en la base de datos, los obtendremos mediante el XML
    try:
        if request.method == 'GET':
            parkingsTodos = Aparcamientos.objects.all() #Obtenemos los 267 aparcamientos
            paginator = Paginator(parkingsTodos, 5) #Mostrara 5 aparcamientos de 5 en 5
            #Obtenemos la pagina de Contactos
            pagina = request.GET.get('page')


            try:
                parkings = paginator.page(pagina)
            except PageNotAnInteger:
                parkings = paginator.page(1)
            except:
                parkings = paginator.page(paginator.num_pages)


            ContentBody = "<ul>"
            for i in parkings:
                botonAñadir = "<form class='Personal' action='/" + str(request.user) + "' method='POST'>" \
                    + "<button type='submit' name='Add' value='" + str(i.id) + "'> Add </button></form>"
                if request.user.is_authenticated():
                    ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a>"+ botonAñadir + "</li>"
                else:
                    ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a></li>"
            ContentBody = ContentBody + "</ul>"
            ContentBody = ContentBody + "<br>"
        elif request.method == 'POST':
            #Obtenemos el keyPOST y el valuePost
            keyPOST, valuePOST = request.body.decode('utf-8').split("=")
            Distrito = valuePOST
            Distrito = unquote_plus(Distrito)
            Distrito = Distrito.upper() #Necesario para que se pueda realziar el filtrado
            if Distrito == 'TODOS':
                parkingsFilter = Aparcamientos.objects.all()
                paginator = Paginator(parkingsFilter, 5) #Mostrara 5 aparcamientos de 5 en 5
                #Obtenemos la pagina de Contactos
                pagina = request.GET.get('page')
                try:
                    parkings = paginator.page(pagina)
                except PageNotAnInteger:
                    parkings = paginator.page(1)
                except:
                    parkings = paginator.page(paginator.num_pages)
            else:
                parkings = Aparcamientos.objects.filter(distrito=Distrito)

            ContentBody = "<ul>"
            for i in parkings:
                botonAñadir = "<form class='Personal' action='/" + str(request.user) + "' method='POST'>" \
                    + "<button type='submit' name='Add' value='" + str(i.id) + "'> Add </button></form>"
                if request.user.is_authenticated():
                    ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a>"+ botonAñadir + "</li>"
                else:
                    ContentBody = ContentBody + "<li><a href='aparcamientos/" + str(i.id) + "'>" + i.nombre + "</a></li>"
            ContentBody = ContentBody + "</li>"


        #Vamos a renderizar
        plantilla = get_template('aparcamientos.html')
        Context = ({'login': header,
                    'enlaces': enlaces,
                    'listado': ContentBody,
                    'filtradoBox': formularioFiltrado,
                    'parkings': parkings})

        return HttpResponse(plantilla.render(Context))
    except Aparcamientos.DoesNotExist:
        plantilla = get_template('error.html')
        botonRecarga = "<form action='recarga' method='GET'>" \
                + "<button type='submit' name='Recargar'> Obtener Aparcamientos</button></form>"
        Context = ({'Contenido' : "No hay Aparcamientos en la base de datos, clicka aqui para obtenerlos" + botonRecarga,
                    'enlaces': enlaces,
                    'login' : header})
        return HttpResponse(plantilla.render(Context))

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
            #Procedemos a renderizar
            plantilla = get_template("info.html")
            Content = ({'login': header,
                        'enlaces': enlaces,
                        'content': Content})
            return HttpResponse(plantilla.render(Content))
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

    Contenido = "<p>PARK es una aplicacion que aglutina informacion sobre los Parkings de Madrid<p>"\
        + "<p>Esta aplicacion te permite si tienes cuenta una serie de funcionalidades, en las que se encuentra" \
        + " comentar los aparcamientos disponibles, dando asi informacion del estado del parking," \
        + "a partir de una pagina personal asociada al usuario, seleccionar aparcamientos que el usuario decida añadir.</p>"\
        + "<p>Las funciones que ofrece para un usario que no tiene contraseña tambien son varias, sin tener cuenta"\
        + " podemos acceder a las paginas de los usuarios, viendo asi, los aparcamientos que ha seleccionado cada usuario" \
        + " , y ver los comentarios que tiene cada Parking de Madrid haciendonos asi una idea del estado de estos</p>" \
        + "<p> Aplicacion implementada por @Javier Fernandez Morata</p>" \
        + "<p> Para sugerencias de como mejorar dicha aplicacion. Enviad Correo a j.fernandezmor@alumnos.urjc.es</p>"

    plantilla = get_template("error.html")
    Content = ({'Contenido': Contenido,
                'login': header,
                'enlaces': enlaces})
    return HttpResponse(plantilla.render(Content))



def obtengoDatos(request):
    #Aqui obtendre los datos de los Aparcamientos y estos seran añadidos en la base de datos

    #Importo la clase creada para usar el xml
    from parking import parseP

    link = 'http://datos.munimadrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos-residentes&mgmtid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&preview=full'
    parseador = parseP.parseadorP(link)
    listaParkings = parseador.listaContenidos()
    for i in listaParkings:
        parseador.obtengoElemento(i)
        addParking(parseador.datos)
    return redirect(barra)

def estiloPropio(request):
    if request.user.is_authenticated():
        usuario = User.objects.get(username=request.user)
        estilo = EstiloUser.objects.get(Usuario=usuario)
        Color = estilo.Color.split("%23")[1].upper()
        Color = "#" + Color
        tamaño = str(estilo.Tamaño) + "mm"
    else:
        Color = "#192666"
        tamaño = "2.80mm"

    plantillaCSS = get_template('personal.css')
    Context = ({'color': Color,
                'tamaño': tamaño})
    return HttpResponse(plantillaCSS.render(Context),content_type="text/css")


@csrf_exempt
def loginUser(request):
    usuario = request.POST['usuario']
    contraseña = request.POST['contraseña']
    user = authenticate(username=usuario, password=contraseña)
    if user is not None:
        login(request, user)
        return redirect(barra)
    else:
        header, loginBol = stringLogin(request)
        #Renderizamos porque no es valido el Usuario
        enlaces = []
        enlaces.append(enlaceInicio)
        enlaces.append(enlaceTodos)
        enlaces.append(enlaceAyuda)
        plantilla = get_template("error.html")
        content = "No es valido el Usuario."
        Context = ({'login': header,
                    'enlaces': enlaces,
                    'Contenido': content})
        return HttpResponse(plantilla.render(Context))


def mylogout(request):
    logout(request)
    return redirect(barra)
