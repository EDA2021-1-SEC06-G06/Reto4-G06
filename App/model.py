﻿"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import haversine as hs
from DISClib.ADT import list as lt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as mp
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra
from DISClib.Algorithms.Sorting import mergesort
from DISClib.Algorithms.Graphs import prim
from DISClib.Algorithms.Graphs import bfs
from ip2geotools.databases.noncommercial import DbIpCity as IP  # Librería para obtener coordenadas de un IP

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos




def newAnalyzer()->dict:
    """Crea el analyzer.

    Returns:
        analyzer: dict
    """

    analyzer = {
        'landingPoints': None,
        'countries': None,
        'infoLandingPoints': None,
        'lista': None,
        'connected': None,
        'paths': None,
        'mst': None
    }

    analyzer['landingPoints'] = gr.newGraph(datastructure='ADJ_LIST', size=14000, comparefunction=cmpLandingPoint, directed=True)

    analyzer['countries'] = mp.newMap(numelements=239, maptype='PROBING')

    analyzer['infoLandingPoints'] = mp.newMap(numelements=1283, maptype='PROBING')

    analyzer['orderedCountries'] = lt.newList('ARRAY_LIST')

    analyzer['lista'] = lt.newList('ARRAY_LIST')  # lista con los landingpoints que se dirigen a ellos mismos.

    analyzer['BFS'] = None

    analyzer['AnchoBanda'] = mp.newMap(numelements=1283, maptype='PROBING')

    return analyzer




# Funciones para agregar informacion al catalogo




def addLandingPointConnection(analyzer, filtered_dict)->dict:
    """
    Agrega al grafo los datos de connections.csv

    Args:
        analyzer
        filtered_dict

    Returns:
        Analyzer
    """

    # Origen, destino, distancia
    origen = filtered_dict['origin'] + '-' + filtered_dict['cable_name']
    destino = filtered_dict['destination'] + '-' + filtered_dict['cable_name']
    distancia = getDistance(analyzer, filtered_dict['origin'], filtered_dict['destination'])

    # Agregar vértices
    addLandingPoint(analyzer, origen)
    addLandingPoint(analyzer, destino)


    #Agregar a la lista
    valueOrigen = mp.get(analyzer['infoLandingPoints'], filtered_dict['origin'])['value']['lista']
    lt.addLast(valueOrigen, origen)
    valueDestino = mp.get(analyzer['infoLandingPoints'], filtered_dict['destination'])['value']['lista']
    lt.addLast(valueDestino, destino)
    # Agregar conexión/arco

    addConnection(analyzer, origen, destino, distancia)
    addConnection(analyzer, destino, origen, distancia)

    addMismoConnection(analyzer, origen)
    addMismoConnection(analyzer, destino)
    return analyzer




def addCapitalLandingPoint(analyzer, filtered_dict):

    """
    Se agrega el nombre de la capital a un landing point

    Args:
        analyzer
        filtered_dict

    Returns:
        Analyzer
    """

    # nombre: Capital-Country

    origen = filtered_dict['CapitalName'] + '-' + filtered_dict['CountryName']

    pais = filtered_dict['CountryName']


    # Conexiones con los del mismo país
    listaMismoPais = listaLandingsMismoPais(analyzer, pais)

    if lt.size(listaMismoPais) == 0:

        masCercano, distancia = findClosest(analyzer, pais)

        for vertice in lt.iterator(gr.vertices(analyzer['landingPoints'])):

            if masCercano in vertice:

                addLandingPoint(analyzer, origen)  # Landing point de la capital.
                addConnection(analyzer, origen, vertice, distancia)
                addConnection(analyzer, vertice, origen, distancia)

            # ---------- ELSE -------------
    else:
        for vertice in lt.iterator(gr.vertices(analyzer['landingPoints'])):

            for landing in lt.iterator(listaMismoPais):  # Cada LandingPoint en la lista (mismo país)

                if landing in vertice:


                    addLandingPoint(analyzer, origen)  # Landing point de la capital.
                    distancia = getDistanceCapital(analyzer, pais, landing)

                    addConnection(analyzer, origen, vertice, distancia)
                    addConnection(analyzer, vertice, origen, distancia)

    return analyzer




def addLandingPoint(analyzer, landingPoint)->dict:
    """
    Adiciona un landing point al grafo.
    """
    if not gr.containsVertex(analyzer['landingPoints'], landingPoint):  # En caso de que el landing point no esté en el grafo, este se agrega.
        gr.insertVertex(analyzer['landingPoints'], landingPoint)

    return analyzer




def addConnection(analyzer, origen, destino, distancia):
    """
    Adiciona un arco entre dos landing points.
    """
    if origen == destino:
        distancia = 0.1

    arco = gr.getEdge(analyzer['landingPoints'], origen, destino)

    if arco is None:
        gr.addEdge(analyzer['landingPoints'], origen, destino, distancia)  # Se agrega la conexión en el grafo, incluyendo los pesos de los arcos.

    return analyzer




def addMismoConnection(analyzer, nombreLP):

    """
    Se agrega un arco de un landing point consigo mismo

    Args:
        analyzer
        nombreLP
    """


    id_ = nombreLP.split('-')[0]


    for lp in lt.iterator(mp.get(analyzer['infoLandingPoints'], id_)['value']['lista']):

        if lp != nombreLP:

            addConnection(analyzer, nombreLP, lp, 0.1)
            addConnection(analyzer, lp, nombreLP, 0.1)  # Se agrega una conexión entre cada LP consigo mismo. 




def listaLandingsMismoPais(analyzer, pais):
    '''
    Retorna un ARRAY_LIST con los landing points en el mismo país de landingPoint
    '''

    listaMismoPais = lt.newList("ARRAY_LIST")

    for uniqueLanding in (lt.iterator(mp.keySet(analyzer['infoLandingPoints']))):

        # get del mapa para la llave

        landing = mp.get(analyzer['infoLandingPoints'], uniqueLanding)['value']  # landing_point_id,id,name,latitude,longitude

        if pais in landing['name']:

            lt.addLast(listaMismoPais, uniqueLanding)  # Agrega el nombre del LandingPoint del país

    return listaMismoPais




def addCountry(analyzer, filtered_dict):
    """
    Agrega un país al mapa.
    """

    if not mp.contains(analyzer['countries'], filtered_dict['CountryName']) and (filtered_dict['CountryName'] is not ''):  # Se agrega cada país único a un mapa.
        mp.put(analyzer['countries'], filtered_dict['CountryName'], filtered_dict)
        lt.addLast(analyzer['orderedCountries'], filtered_dict['CountryName'])

    return analyzer




def lastCountry(analyzer, lista):

    """
    Se agrega el último país que se cargó en el analyzer a una lista

    Args:
        analyzer
        lista

    Returns:
        El último país cargado en el grafo
    """

    pais = lt.lastElement(lista)

    valores = mp.get(analyzer['countries'], pais) #  Se obteiene el último país cargado, junto conn su respectiva infromación.

    return valores




def addMapLandingPoint(analyzer, filtered_dict):
    '''
    Agrega info de cada Landing Point único (Sin cable).
    '''
    filtered_dict['lista'] = lt.newList('ARRAY_LIST')

    if not mp.contains(analyzer['infoLandingPoints'], filtered_dict['landing_point_id']) and (filtered_dict['landing_point_id'] is not ''):
        mp.put(analyzer['infoLandingPoints'], filtered_dict['landing_point_id'], filtered_dict)  # Se agrega la información de cada LP único en el mapa.

    return analyzer




def connectedComponents(analyzer)->int:
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """

    analyzer['connected'] = scc.KosarajuSCC(analyzer['landingPoints'])  # Se utiliza Kosaraju para encontrar los componentes conectados en el grafo.

    return scc.connectedComponents(analyzer['connected'])




# Funciones para creacion de datos




def getDistanceCapital(analyzer, pais, destino):
    '''
    Calcula la distancia entre la capital de un país y otro destino.
    '''
    dictOrigen = mp.get(analyzer['countries'], pais)['value']
    dictDestino = mp.get(analyzer['infoLandingPoints'], destino)['value']


    location1 = (dictOrigen['CapitalLatitude'], dictOrigen['CapitalLongitude'])



    location2 = (dictDestino['latitude'], dictDestino['longitude'])  # Se obtuvo la latitud y la longitud tanto del origen como del detino.

    return hs.haversine(location1, location2)  # Se calcula la distancia entre ambas capitales.




def getDistance(analyzer, origen, destino):
    """Calcula la distancia entre dos Landing Points.

    Args:
        analyzer: [description]
        origen : [description]
        destino : [description]

    Returns:
        float: La distancia.
    """

    dictOrigen = mp.get(analyzer['infoLandingPoints'], origen)['value']
    dictDestino = mp.get(analyzer['infoLandingPoints'], destino)['value']


    location1 = (dictOrigen['latitude'], dictOrigen['longitude'])

    location2 = (dictDestino['latitude'], dictDestino['longitude'])  # Se obtuvo la latitud y la longitud tanto del origen como del detino.

    return hs.haversine(location1, location2)  # Se calcula la distancia entre ambos LP.




def haversine(tupla1, tupla2):
    """
    Calcula la distancia entre dos LP de acuerdo a la latitud y longitud. 
    """

    return hs.haversine(tupla1, tupla2)




def findClosest(analyzer, pais):
    """
    Encuentra el landing point más cercano a un país. 

    Args:
        analyzer
        país

    Returns:
        menor menorValor
    """
    dictOrigen = mp.get(analyzer['countries'], pais)['value']
    location1 = (dictOrigen['CapitalLatitude'], dictOrigen['CapitalLongitude'])


    menor = None
    menorValor = 999999999

    for landingPoint in lt.iterator(mp.keySet(analyzer['infoLandingPoints'])):  # Se encuentra el LP más cercano al país.

        dictDestino = mp.get(analyzer['infoLandingPoints'], landingPoint)['value']
        location2 = (dictDestino['latitude'], dictDestino['longitude'])


        if hs.haversine(location1, location2) < menorValor:
            menorValor = hs.haversine(location1, location2)

            menor = landingPoint # str

    return menor, menorValor




def minimumCostPaths(analyzer, paisA):
    """
    Calcula los caminos de costo mínimo desde la capital del país A a todos los demás vértices.
    """

    capitalPaisA = mp.get(analyzer['countries'], paisA)['value']

    nombrePaisA = capitalPaisA['CapitalName'] + '-' + capitalPaisA['CountryName']  # Nombre del LP en el grafo.

    analyzer['paths'] = dijsktra.Dijkstra(analyzer['landingPoints'], nombrePaisA)  # Se utiliza Dijkstra con el paísA para después encontrar la ruta de menor costo hacia paísB.

    return analyzer




def hasPath(analyzer, paisB):
    """
    Indica si existe un camino desde el país base a país B.
    Se debe ejecutar primero la funcion minimumCostPaths
    """

    capitalPaisB = mp.get(analyzer["countries"], paisB)["value"]  # PAIS B

    nombrePaisB = capitalPaisB['CapitalName'] + '-' + capitalPaisB['CountryName']
    return dijsktra.hasPathTo(analyzer['paths'], nombrePaisB)  # Se confirma que exista un camnino entre paísA y paísB




def minimumCostPath(analyzer, paisB):

    """
    Encuentra el camino de costo mínimo entre un país A (previamente cargado )y un país B.

    Args:
        analyzer
        paisB

    Returns:
        El menor camino entre país A y el país B.
    """

    capitalPaisB = mp.get(analyzer["countries"], paisB)["value"]  # PAIS B

    nombrePaisB = capitalPaisB['CapitalName'] + '-' + capitalPaisB['CountryName']

    return dijsktra.pathTo(analyzer['paths'], nombrePaisB)  # Se obtiene el path entre paísA y paísB




def mstPRIM(analyzer):
    '''
    Recibe un grafo como parámetro y retorna
    '''
    analyzer['mst'] = prim.PrimMST(analyzer['landingPoints'])




def loadBFS(analyzer):
    '''
    Hace un BFS de analyzer['landingPoints'], desde 'Bogota-Colombia'.
    '''
    analyzer['BFS'] = bfs.BreadhtFisrtSearch(analyzer['landingPoints'], 'Bogota-Colombia')




# Funciones de consulta




def requerimiento1(analyzer, vertexA:str, vertexB:str):
    '''
    Se desea encontrar la cantidad de clústeres (componentes conectados) dentro de la red de cables submarinos y si dos landing points pertenecen o no al mismo clúster.
    Para dar respuesta a este requerimiento el equipo de desarrollo debe recibir como entrada la siguiente información:
        • Nombre del landing point 1
        • Nombre del landing point 2
    Y como respuesta debe presentar en consola la siguiente información:
        • Número total de clústeres presentes en la red
        • Informar si los dos landing points están en el mismo clúster o no
    '''
    datosCluster = analyzer['connected']['idscc']

    valorVertexA = None
    valorVertexB = None


    for landingID in lt.iterator(mp.keySet(analyzer['infoLandingPoints'])):  # Cada número que es el landing point id

        if vertexA in mp.get(analyzer['infoLandingPoints'], landingID)['value']['name']:   # si la ciudad está en el name de landingID

            for vertice in lt.iterator(mp.keySet(datosCluster)):  #Por cada vértice en el grafo con los componentes conectados

                if landingID in vertice:  # si el número está en el nombre del vértice
                    valorVertexA = mp.get(datosCluster, vertice)['value']
                    infoLP1 = vertice


        if vertexB in mp.get(analyzer['infoLandingPoints'], landingID)['value']['name']:  # Lo mismo

            for vertice in lt.iterator(mp.keySet(datosCluster)):
                if landingID in vertice:
                    valorVertexB = mp.get(datosCluster, vertice)['value']
                    infoLP2 = vertice

        if valorVertexA is not None and valorVertexB is not None:  # Si ambos son None

            return (((valorVertexA) == (valorVertexB)), (infoLP1, infoLP2))

    return (False, False)




def req2(analyzer):
    '''
    Retorna una lista ordenada según la cantidad de arcos de cada vértice.
    '''
    numMayor = 0
    listaArcos = lt.newList("ARRAY_LIST")  # Lista para sacar el vértice con más arcos, puesto que es necesario recorrer todos.
    
    for vertex in lt.iterator(gr.vertices(analyzer['landingPoints'])):
        adyacentes = gr.adjacentEdges(analyzer['landingPoints'], vertex)

        if lt.size(adyacentes) >= numMayor:

            numMayor = lt.size(adyacentes)  # Cuando se encuentra el vértice con más arcos se obtienen sus adyacentes.

            verticeArcos = {
                'vertice': vertex,
                'size': numMayor
            }
            lt.addLast(listaArcos, verticeArcos)

    return sortNumEdgesReq2(listaArcos)   # Se realiza un Merge Sort de los LP con más adyacentes.



def getDistanceREQ3(analyzer, vertex):


    infoLP = analyzer['infoLandingPoints']

    infoCapital = analyzer['countries']
    
    infoPais = mp.get(infoLP, vertex.split('-')[0])

    if infoPais is not None:

        coordenadas = (infoPais['value']["latitude"], infoPais['value']['longitude'])

        return coordenadas

    else:
        infoPais = mp.get(infoCapital, vertex.split('-')[1])

        coordenadas = (infoPais['value']['CapitalLatitude'], infoPais['value']['CapitalLongitude'])

        return coordenadas
        



def req4(analyzer):
    """
    Encuentra el mayor recorrido entre Bogotá-Colombia con los demás LP del grafo

    Args:
        analyzer

    Returns:
        numNodos, distanciaTotal, mayorRecorrido
    """

    numNodos = mp.size(analyzer['mst']['distTo'])  # Se obtiene el número de nodos conectados a la red de expansión mínima.
    distanciaTotal = 0

    mayorRecorrido = 0

    for llaveValor in lt.iterator(mp.keySet(analyzer['mst']['distTo'])):
        # Ejemplo {'key': '10985-Malaysia-Cambodia-Thailand (MCT) Cable', 'value': 145.54934328686224}
        verticeValor = mp.get(analyzer['mst']['distTo'], llaveValor)['value']

        if verticeValor is not None:
            distanciaTotal += verticeValor  # Se obtiene el costo total de la red de expansión mínima.

    return (numNodos, distanciaTotal, mayorRecorrido)




def bfsReq4(analyzer):
    """Retorna un dict que es la rama más larga con su landing Point final.

    Args:
        analyzer

    Returns:
        infoRama[dict]: Rama con mayor longitud.
    """
    newBFS = analyzer["BFS"]  # BFS del grafo con el vétrtice Bogota-Colombia.

    distanciaMax = 0  # Se inicia la distancia máxima en 0.

    infoRama = None

    for element in (newBFS['visited']['table']['elements']):  # Por cada elemento se extrae su valor.
        distancia = element['value']
        
        if distancia is not None:

            if distancia['distTo'] > distanciaMax:  # Se compara la distancua máxima con la del elemento actual.

                distanciaMax = distancia['distTo']
                infoRama = element['value']
    
    path = bfs.pathTo(newBFS, infoRama['edgeTo'])

    return (infoRama, path)  # Se retorna la infromación del LP con mayor distancia de Bogota-Colombia.




def req5(analyzer, inputLP):
    """Recibe un LP de interés. Retorna una lista de los países (adyacentes) ordenados descendentemente según su distancia.

    Args:
        analyzer
        inputLP (str): Landing Point de interés del usuario.

    Returns:
        sorted_list (ARRAY_LIST): Lista ordenada.
    """
    verticesConectados = gr.adjacents(analyzer['landingPoints'], inputLP)  # Se obtienen los adyacentes del LP que entra por parámetro.

    numeros = '0123456789'
    
    listaPaisesAfectados = lt.newList('ARRAY_LIST')
    
    for lp in lt.iterator(verticesConectados):

        if lp[0] not in numeros:

            pais = {
                'nombre': lp.split('-')[1],
                'weight': gr.getEdge(analyzer['landingPoints'], inputLP, lp)['weight']
            }
            
            lt.addLast(listaPaisesAfectados, pais)  # Se agregan los LP adyacentes en una lista.

            

    return sortMenorDistancia(listaPaisesAfectados)



def infoVertex(analyzer, inputLP):
    id_ = inputLP.split('-')[0]
    vertice = mp.get(analyzer['infoLandingPoints'],id_)
    return (vertice['value']["latitude"], vertice['value']["longitude"])


def req6(analyzer, nombrePais, nombreCable)->tuple:
    """Realiza las operaciones del req6 para obtener los países y el ancho de banda del cable.

    Args:
        analyzer ([type]): [description]
        nombrePais ([type]): [description]
        nombreCable ([type]): [description]

    Returns:
        tuple: (listaPaises, anchoDeBanda)
    """

    nombrePais = mp.get(analyzer['countries'], nombrePais)['value']
    nombrePais = nombrePais['CapitalName']+'-'+nombrePais['CountryName']  # Nombre del LP del país como aparece en el grafo

    anchoDeBandaCable = mp.get(analyzer['AnchoBanda'], nombreCable)['value']  # Ancho de banda del cable.

    lista = lt.newList("ARRAY_LIST")
    mapa = mp.newMap(maptype="PROBING", numelements=31)

    recursiva(analyzer, nombrePais, nombreCable, lista, mapa, nombrePais)  # Función recursiva para agregarle los países a la lista "lista"

    return lista, anchoDeBandaCable




def req7(ip1, ip2, analyzer):
    """Encuentra si existe un path entre ip1 e ip2

    Args:
        analyzer
        ip1: Primera dirección de IP
        ip2: Segunda dirección de IP
    """
    responseip1 = IP.get(ip1, api_key='free')  # Se obtiene la información de ip1
    responseip2 = IP.get(ip2, api_key='free')  # Se obtiene la información de ip2

    latitudeIP1 = responseip1.latitude   # Se obtiene la latitud de ip1
    longitudeIP1 = responseip1.longitude    # Se obtiene la longitud de ip1
    latitudeIP2 = responseip2.latitude    # Se obtiene la latitud de ip2
    longitudeIP2 = responseip2.longitude  # Se obtiene la longitud de ip2

    masCercano_1 = lpMasCercano(analyzer, latitudeIP1, longitudeIP1)[1]

    
    lp1 = lt.getElement(mp.get(analyzer['infoLandingPoints'], masCercano_1)['value']['lista'], 1)
    
    
    masCercano_2 = lpMasCercano(analyzer, latitudeIP2, longitudeIP2)[1]
    lp2 = lt.getElement(mp.get(analyzer['infoLandingPoints'], masCercano_2)['value']['lista'], 1)


    varBFS = bfs.BreadhtFisrtSearch(analyzer['landingPoints'], lp1)
    
    if bfs.hasPathTo(varBFS, lp2) is True:  # Si existe un path se retorna la distancia entre el LP destino y origen, junto con el path entre estos dos.
        distancia  = rutaReq7(varBFS, lp2)
        path = bfs.pathTo(varBFS, lp2)
        return (distancia['distTo'], path)

    else:
        return False  # En caso de que no encuentre un path la función retorna False.




def path(analyzer, INFOlp1, INFOlp2):

    varBFS = bfs.BreadhtFisrtSearch(analyzer['landingPoints'], INFOlp1)
    
    if bfs.hasPathTo(varBFS, INFOlp2) is True:  # Si existe un path se retorna la distancia entre el LP destino y origen, junto con el path entre estos dos.
        path = bfs.pathTo(varBFS, INFOlp2)
        return path




def rutaReq7(bfs, lp2):
    """
    Encuentra la ruta entre un landing point 1 (previamente establecido) y el landing point 2.

    Args:
        bfs
        lp2

    Returns:
        infoRama
    """
    
    infoRama = None

    for element in (bfs['visited']['table']['elements']):  # Por cada elemento se extrae su valor.
        landingPoint = element['key']

        if (element['value'] is not None) and (element['value']['edgeTo'] == lp2):
            infoRama = element['value']
    
    return (infoRama)




def lpMasCercano(analyzer, latitud, longitud):
    '''
    Retorna (menorDistancia, menorLP)
    '''

    menorDistancia = 999999999
    menor = None
    for lp in lt.iterator(mp.keySet(analyzer['infoLandingPoints'])):
        #{'key': '4219', 'value': {'landing_point_id': '4219', 'id': 'kingstown-saint-vincent-and-the-grenadines', 'name': 'Kingstown, Saint Vincent and the Grenadines', 'latitude': 13.145437, 'longitude': -61.208256, 'lista': {'elements': ['4219-Caribbean Regional Communications Infrastructure Program (CARCIP)',
        valorLP = mp.get(analyzer['infoLandingPoints'], lp)['value']

        distancia = haversine((latitud, longitud), (valorLP['latitude'], valorLP['longitude']))

        if menorDistancia > distancia:  # Encuentra el LP más cercano y se guarda su información.

            menorDistancia = distancia
            menor = mp.get(analyzer['infoLandingPoints'], lp)['key']

    return menorDistancia, menor




def recursiva(analyzer, vertex, cable, lista, mapa, original)->None:
    """Función recursiva para encontrar los países del req6.

    Args:
        analyzer
        vertex (str): Vértice A
        cable (str): Nombre del cable.
        lista (ARRAY_LIST): Lista con los países.
        mapa (Hash Map): Mapa que contiene los vértices que ya han sido buscados.
        original (str): Vértice original.
    """

    for arco in lt.iterator(gr.adjacentEdges(analyzer['landingPoints'], vertex)):

        if arco['vertexB'][0] not in '1234567890' and arco['vertexB'] != original:  # Si no empieza en un número

            lt.addLast(lista, arco['vertexB'])  # Se agrega a la lista que es la que retorna la función "req6"

        if cable in arco['vertexB'] and not mp.contains(mapa, arco['vertexB']):
            mp.put(mapa, arco['vertexB'], None)
            recursiva(analyzer, arco['vertexB'], cable, lista, mapa, original)  # Si tiene el cable repite el proceso.




def mapaAnchodeBanda(analyzer, cable, anchodeBanda):
    """
    Se agrega a un mapa el ancho de banda de cada cable.

    Args:
        analyzer
        cable
        anchodeBanda
    """

    mp.put(analyzer['AnchoBanda'], cable, anchodeBanda)




# Funciones utilizadas para comparar elementos dentro de una lista




def cmpLandingPoint(l1, l2):
    """
    Compara el nombre de dos landing points.
    """
    l2 = l2['key']
    if l1 == l2:
        return 0
    elif l1 > l2:
        return 1
    else:
        return -1




def cmpNumEdgesReq2(verticeA, verticeB):
    """
    Compara el número de arcos de dos landing points.
    """
    return (verticeA['size'] > verticeB['size'])




def cmpMenorDistancia(paisA, paisB):
    """
    Compara distancias entre dos países. 
    """
    return (paisA['weight'] < paisB['weight'])




# Funciones de ordenamiento



def sortNumEdgesReq2(listaVerticesArcos):
    '''
    Retorna una lista con los vértices ordenados según su cantidad de arcos.
    '''
    sub_list = lt.subList(listaVerticesArcos, 1, lt.size(listaVerticesArcos))
    sub_list = sub_list.copy()

    sorted_list = mergesort.sort(sub_list, cmpNumEdgesReq2)

    return sorted_list




def sortMenorDistancia(listaPaises):
    '''
    Retorna una lista de los países según su distancia en orden descendente.
    '''
    sub_list = lt.subList(listaPaises, 1, lt.size(listaPaises))
    sub_list = sub_list.copy()

    sorted_list = mergesort.sort(sub_list, cmpMenorDistancia)
    return sorted_list