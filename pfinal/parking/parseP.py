#!/usr/bin/python3
from urllib.request import *
from bs4 import BeautifulSoup as BS

class parseadorP:

    xmlTree = ""
    datos = {'NOMBRE': None ,'DESCRIPCION': None,'ACCESIBILIDAD': None,'CONTENT-URL': None,'NOMBRE-VIA': None,
             'CLASE-VIAL': None,'BARRIO':None,'DISTRITO':None ,'LATITUD':None ,'LONGITUD':None ,
             'TELEFONO':None,'EMAIL':None}

    def __init__(self,url):
        #Obtengo el XML y de este el arbol

        xmlString = urlopen(url).read().decode('utf-8')
        self.xmlTree = BS(xmlString,"html.parser")

    def listaContenidos(self):
        #Obtengo todos los contenidos del XML,es decir, todos los aparcamientos

        lista = self.xmlTree.find_all('contenido')
        return lista

    def obtengoElemento(self, listaAtributos):
        #Obtengo un diccionario con los datos que me interesan

        listaAtributos = listaAtributos.find_all('atributo')
        for i in listaAtributos:
            if i['nombre'] in self.datos.keys():
                self.datos[i['nombre']] = i.string


########################################AQUI PROBAREMOS EL PROGRAMA###################################################################
# enlace lectura ->
# http://datos.munimadrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos-residentes&mgmtid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&preview=full
if __name__ == "__main__":
    x = parseadorP('http://datos.munimadrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos-residentes&mgmtid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&preview=full')
    listaAparcamientos = x.listaContenidos()
    #Bucle para probar el arbol
    for i in listaAparcamientos:
        x.obtengoElemento(i)
