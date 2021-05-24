"""
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
        'capacity': None,
        'lista': None,
        'connected': None
    }

    analyzer['landingPoints'] = gr.newGraph(datastructure='ADJ_LIST', directed=False, size=14000, comparefunction=cmpLandingPoint)

    analyzer['capacity'] = gr.newGraph(datastructure='ADJ_LIST', directed=False, size=14000, comparefunction=cmpLandingPoint)

    analyzer['countries'] = mp.newMap(numelements=239, maptype='PROBING')

    analyzer['infoLandingPoints'] = mp.newMap(numelements=1283, maptype='PROBING')

    analyzer['orderedCountries'] = lt.newList('ARRAY_LIST')

    analyzer['lista'] = lt.newList('ARRAY_LIST')  # lista con los landingpoints que se dirigen a ellos mismos.

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

    # Agregar conexión/arco

    addConnection(analyzer, origen, destino, distancia)

    return analyzer




def addCapacityTBPSConnection(analyzer, filtered_dict: dict)->dict:
    """
    Agrega al grafo los datos de connections.csv. PESO = CAPACIDAD TBPS

    Args:
        analyzer
        filtered_dict

    Returns:
        Analyzer
    """
    # Origen, destino, distancia
    origen = filtered_dict['origin'] + '-' + filtered_dict['cable_name']
    destino = filtered_dict['destination'] + '-' + filtered_dict['cable_name']

    anchoDeBanda = filtered_dict['capacityTBPS']

    # Agregar vértices
    addLandingPointTBPS(analyzer, origen)
    addLandingPointTBPS(analyzer, destino)

    # Agregar conexión/arco

    addConnectionTBPS(analyzer, origen, destino, anchoDeBanda)

    return analyzer




def addCapitalLandingPoint(analyzer, filtered_dict):

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
                
            # ---------- ELSE -------------
    else:
        for vertice in lt.iterator(gr.vertices(analyzer['landingPoints'])):

            for landing in lt.iterator(listaMismoPais):  # Cada LandingPoint en la lista (mismo país)

                if landing in vertice:

                
                    addLandingPoint(analyzer, origen)  # Landing point de la capital.
                    distancia = getDistanceCapital(analyzer, pais, landing)
                    
                    addConnection(analyzer, origen, vertice, distancia)
            
    return analyzer




def addCapitalLandingPointTBPS(analyzer, filtered_dict):

    # nombre: Capital-Country

    origen = filtered_dict['CapitalName'] + '-' + filtered_dict['CountryName']

    pais = filtered_dict['CountryName']



    # Conexiones con los del mismo país
    listaMismoPais = listaLandingsMismoPais(analyzer, pais)

    if lt.size(listaMismoPais) == 0:

        masCercano, distancia = findClosest(analyzer, pais)


        for vertice in lt.iterator(gr.vertices(analyzer['capacity'])):
            
            if masCercano in vertice:

                menor = menorBandaAncha(analyzer, vertice)
                
                addLandingPointTBPS(analyzer, origen)  # Landing point de la capital.
                
                addConnectionTBPS(analyzer, origen, vertice, menor)
                
            # ---------- ELSE -------------
    else:

        
        for vertice in lt.iterator(gr.vertices(analyzer['capacity'])):

            for landing in lt.iterator(listaMismoPais):  # Cada LandingPoint en la lista (mismo país)

                if landing in vertice:
                    
                    menor = menorBandaAncha(analyzer, vertice)
                
                    addLandingPointTBPS(analyzer, origen)  # Landing point de la capital.
                    
                    addConnectionTBPS(analyzer, origen, vertice, menor)
                    
      
    return analyzer




def addLandingPoint(analyzer, landingPoint)->dict:
    """
    Adiciona un landing point al grafo.
    """
    if not gr.containsVertex(analyzer['landingPoints'], landingPoint):
        gr.insertVertex(analyzer['landingPoints'], landingPoint)

    return analyzer




def addLandingPointTBPS(analyzer, landingPoint)->dict:
    """ 
    Adiciona un landing point al grafo capacity.
    """
    if not gr.containsVertex(analyzer['capacity'], landingPoint):
        gr.insertVertex(analyzer['capacity'], landingPoint)

    return analyzer




def addConnection(analyzer, origen, destino, distancia):
    """
    Adiciona un arco entre dos landing points.
    """
    if origen == destino:
        distancia = 0.1
    
    arco = gr.getEdge(analyzer['landingPoints'], origen, destino)

    if arco is None:
        gr.addEdge(analyzer['landingPoints'], origen, destino, distancia)

    return analyzer




def addConnectionTBPS(analyzer, origen, destino, capacidad):
    '''
    Adiciona un arco entre dos landing points al grafo capacity
    '''
    lista = analyzer['lista']

    if origen == destino:
        lt.addLast(lista, origen)
        
    
    else:
        arco = gr.getEdge(analyzer['capacity'], origen, destino)

        if arco is None:
            gr.addEdge(analyzer['capacity'], origen, destino, capacidad)

        return analyzer
    



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

    if not mp.contains(analyzer['countries'], filtered_dict['CountryName']) and (filtered_dict['CountryName'] is not ''):
        mp.put(analyzer['countries'], filtered_dict['CountryName'], filtered_dict)
        lt.addLast(analyzer['orderedCountries'], filtered_dict['CountryName'])

    return analyzer




def lastCountry(analyzer, lista):

    pais = lt.lastElement(lista)

    valores = mp.get(analyzer['countries'], pais)

    return valores




def addMapLandingPoint(analyzer, filtered_dict):
    '''
    Agrega info de cada Landing Point único (Sin cable).
    '''

    if not mp.contains(analyzer['infoLandingPoints'], filtered_dict['landing_point_id']) and (filtered_dict['landing_point_id'] is not ''):
        mp.put(analyzer['infoLandingPoints'], filtered_dict['landing_point_id'], filtered_dict)

    return analyzer




def loadTBPSRepetidos(analyzer)->None:
    """Función para agregar un arco al landingpoing que se repita en el grafo de conectivity.

    Args:
        analyzer: El analyzer.
    """

    lista = analyzer['lista']
    
    for landingPoint in lt.iterator(lista):

        for arco in lt.iterator(gr.adjacentEdges(analyzer['capacity'], landingPoint)):

            minimo = 99999999
            
            if arco['weight'] < minimo:  # Menor de los arcos adjacentes al vértice.
                minimo = arco['weight']

        gr.addEdge(analyzer['capacity'], landingPoint, landingPoint, minimo)




def menorBandaAncha(analyzer, vertice)->float:
    """Retorna la menor banda ancha de los vértices más cercanos.


    Returns:
        float: Menor valor.
    """
    menor = 999999

    for arco in lt.iterator(gr.adjacentEdges(analyzer['capacity'], vertice)):

        if arco['weight'] < menor:
            menor = arco['weight']

    return menor




def connectedComponents(analyzer)->int:
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """

    analyzer['connected'] = scc.KosarajuSCC(analyzer['landingPoints'])

    return scc.connectedComponents(analyzer['connected'])

# Funciones para creacion de datos


def getDistanceCapital(analyzer, pais, destino):
    '''
    Calcula la distancia entre la capital de un país y otro destino.
    '''
    dictOrigen = mp.get(analyzer['countries'], pais)['value']
    dictDestino = mp.get(analyzer['infoLandingPoints'], destino)['value']

    
    location1 = (dictOrigen['CapitalLatitude'], dictOrigen['CapitalLongitude'])

    

    location2 = (dictDestino['latitude'], dictDestino['longitude'])

    return hs.haversine(location1, location2)




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

    location2 = (dictDestino['latitude'], dictDestino['longitude'])

    return hs.haversine(location1, location2)
    

    

def findClosest(analyzer, pais):
    dictOrigen = mp.get(analyzer['countries'], pais)['value']
    location1 = (dictOrigen['CapitalLatitude'], dictOrigen['CapitalLongitude'])


    menor = None
    menorValor = 999999999

    for landingPoint in lt.iterator(mp.keySet(analyzer['infoLandingPoints'])):

        dictDestino = mp.get(analyzer['infoLandingPoints'], landingPoint)['value']
        location2 = (dictDestino['latitude'], dictDestino['longitude'])


        if hs.haversine(location1, location2) < menorValor:
            menorValor = hs.haversine(location1, location2)

            menor = landingPoint # str

    return menor, menorValor
            
        

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

        
        if vertexB in mp.get(analyzer['infoLandingPoints'], landingID)['value']['name']:  # Lo mismo

            for vertice in lt.iterator(mp.keySet(datosCluster)):
                if landingID in vertice:
                    valorVertexB = mp.get(datosCluster, vertice)['value']

        if valorVertexA is not None and valorVertexB is not None:  # Si ambos son None
    
            return ((valorVertexA) == (valorVertexB))

    return False




def req2(analyzer):
    '''
    Retorna una lista ordenada según la cantidad de arcos de cada vértice.
    '''
    numMayor = 0
    listaArcos = lt.newList("ARRAY_LIST")
    
    for vertex in lt.iterator(gr.vertices(analyzer['landingPoints'])):
        adyacentes = gr.adjacentEdges(analyzer['landingPoints'], vertex)

        if lt.size(adyacentes) >= numMayor:

            numMayor = lt.size(adyacentes)

            verticeArcos = {
                'vertice': vertex,
                'size': numMayor
            }
            lt.addLast(listaArcos, verticeArcos)

    return sortNumEdgesReq2(listaArcos)
        
# Funciones utilizadas para comparar elementos dentro de una lista

def cmpLandingPoint(l1, l2):

    l2 = l2['key']
    if l1 == l2:
        return 0
    elif l1 > l2:
        return 1
    else:
        return -1



def cmpNumEdgesReq2(verticeA, verticeB):
    return (verticeA['size'] > verticeB['size'])
# Funciones de ordenamiento


def sortNumEdgesReq2(listaVerticesArcos):
    '''
    Retorna una lista con los vértices ordenados según su cantidad de arcos.
    '''
    sub_list = lt.subList(listaVerticesArcos, 1, lt.size(listaVerticesArcos))
    sub_list = sub_list.copy()

    sorted_list = mergesort.sort(sub_list, cmpNumEdgesReq2)

    return sorted_list