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
 """

import config as cf
import model
import csv
assert cf

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros




def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer




# Funciones para la carga de datos




def loadConnectionsCSV(analyzer):
    '''
    Se carga la información del CSV de connections.csv
    '''
    landingPointsFile = cf.data_dir + 'connections.csv'
    input_file = csv.DictReader(open(landingPointsFile, encoding='utf-8-sig'), delimiter=',')

    # lastLandingPoint ??
    centinela = True

    for landingPoint in input_file:
        # origin,destination,cable_name,cable_id,cable_length,cable_rfs,owners,capacityTBPS

        filtered_dict = {
            'origin': landingPoint['origin'],
            'destination': landingPoint['destination'],
            'cable_name': landingPoint['cable_name'],
            'cable_id': landingPoint['cable_id'],
            'cable_length': landingPoint['cable_length'],
            'capacityTBPS': landingPoint['capacityTBPS']
        }

        if filtered_dict['cable_length'] == 'n.a.':
            filtered_dict['cable_length'] = 0
        else:
            filtered_dict['cable_length'] = float((landingPoint['cable_length'].replace(' km', '')).replace(',', ''))

        if centinela:
            first = filtered_dict
            centinela = False

        if filtered_dict['capacityTBPS'] is not '':
            filtered_dict['capacityTBPS'] = float(filtered_dict['capacityTBPS'])

            model.addLandingPointConnection(analyzer, filtered_dict)
            model.mapaAnchodeBanda(analyzer, filtered_dict['cable_name'], filtered_dict['capacityTBPS'])

    return first




def loadCountries(analyzer):
    '''
    Se carga la información del CSV de countries.csv
    '''
    countriesFile = cf.data_dir + 'countries.csv'
    input_file = csv.DictReader(open(countriesFile, encoding='utf-8-sig'), delimiter=',')


    for country in input_file:
        # CountryName,CapitalName,CapitalLatitude,CapitalLongitude,CountryCode,ContinentName,Population,Internet users
        filtered_dict = {
            'CountryName': country['CountryName'],
            'CapitalName': country['CapitalName'],
            'CapitalLatitude': (country['CapitalLatitude']),
            'CapitalLongitude': (country['CapitalLongitude']),
            'CountryCode': country['CountryCode'],
            'ContinentName': country['ContinentName'],
            'Population': float(country['Population'].replace('.','')),
            'Internet users': float(country['Internet users'].replace('.',''))
        }

        if filtered_dict['CapitalLatitude'] is not '':
            filtered_dict['CapitalLatitude'] = float(filtered_dict['CapitalLatitude'])

        if filtered_dict['CapitalLongitude'] is not '':
            filtered_dict['CapitalLongitude'] = float(filtered_dict['CapitalLongitude'])

        if filtered_dict['CountryName'] is not '':
            model.addCountry(analyzer, filtered_dict)
            model.addCapitalLandingPoint(analyzer, filtered_dict)

    resultado = model.lastCountry(analyzer, analyzer['orderedCountries'])
    analyzer['orderedCountries'] = None # Somos fancy y nos gusta el espacio en memoria
    return resultado




def loadLandingPoints(analyzer):
    '''
    Se carga la información del CSV de landing_points.csv
    '''
    
    landingPointsFile = cf.data_dir + 'landing_points.csv'

    input_file = csv.DictReader(open(landingPointsFile, encoding='utf-8-sig'), delimiter=',')

    centinela = True

    for landingPoint in input_file:
        # landing_point_id,id,name,latitude,longitude
        filtered = {
            'landing_point_id': landingPoint['landing_point_id'],
            'id': landingPoint['id'],
            'name': landingPoint['name'],
            'latitude': float(landingPoint['latitude']),
            'longitude': float(landingPoint['longitude'])
        }
        if centinela:
            firstLatitude = float(landingPoint['latitude'])
            firstLongitude = float(landingPoint['longitude'])
            centinela = False

        model.addMapLandingPoint(analyzer, filtered)

    return (firstLatitude, firstLongitude)




def loadBFS(analyzer):
    '''
    Hace un BFS de analyzer['landingPoints'], desde 'Bogota-Colombia'.
    '''
    model.loadBFS(analyzer)



    
# Funciones de ordenamiento




# Funciones de consulta sobre el catálogo




def connectedComponents(analyzer)->int:
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    return model.connectedComponents(analyzer=analyzer)




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

    return model.requerimiento1(analyzer, vertexA, vertexB)




def req2(analyzer):
    '''
    Retorna una lista ordenada según la cantidad de arcos de cada vértice.
    '''
    return model.req2(analyzer)




def req4(analyzer):
    """
    Encuenntra el mayor recorrido entre Bogotá-Colombia con los demás LP del grafo

    Args:
        analyzer

    Returns:
        numNodos, distanciaTotal, mayorRecorrido
    """
    return model.req4(analyzer)




def bfsReq4(analyzer):
    """Retorna un dict que es la rama más larga con su landing Point final.

    Args:
        analyzer

    Returns:
        infoRama[dict]: Rama con mayor longitud.
    """
    return model.bfsReq4(analyzer)




def req5(analyzer, inputLP):
    """Recibe un LP de interés. Retorna una lista de los países (adyacentes) ordenados descendentemente según su distancia.

    Args:
        analyzer
        inputLP (str): Landing Point de interés del usuario.

    Returns:
        sorted_list (ARRAY_LIST): Lista ordenada.
    """
    return model.req5(analyzer, inputLP)


def infoVertex(analyzer, inputLP):
    return model.infoVertex(analyzer, inputLP)




def req6(analyzer, nombrePais, nombreCable)->tuple:
    """Realiza las operaciones del req6 para obtener los países y el ancho de banda del cable.

    Args:
        analyzer ([type]): [description]
        nombrePais ([type]): [description]
        nombreCable ([type]): [description]

    Returns:
        tuple: (listaPaises, anchoDeBanda)
    """
    return model.req6(analyzer, nombrePais, nombreCable)




def req7(ip1, ip2, analyzer):
    """Encuentra si existe un path entre ip1 e ip2

    Args:
        analyzer
        ip1: Primera dirección de IP
        ip2: Segunda dirección de IP
    """
    return model.req7(ip1, ip2, analyzer)



def path(analyzer, INFOlp1, INFOlp2):
    """Encuentra si existe un path entre ip1 e ip2

    Args:
        analyzer
        lp1: Nombre del primer LP
        lp2: Nombre del segundo lP
    """
    return model.path(analyzer, INFOlp1, INFOlp2)



def minimumCostPaths(analyzer, paisA):
    """
    Calcula los caminos de costo mínimo desde la capital del país A a todos los demás vértices.
    """

    return model.minimumCostPaths(analyzer, paisA)



def getDistanceREQ3(analyzer, vertex):

    return model.getDistanceREQ3(analyzer, vertex)


def hasPath(analyzer, paisB):
    """
    Indica si existe un camino desde el país base a país B.
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    return model.hasPath(analyzer, paisB)


def haversine(tupla1, tupla2):
    """
    Calcula la distancia entre dos LP de acuerdo a la latitud y longitud. 
    """

    return model.haversine(tupla1, tupla2)



def minimumCostPath(analyzer, paisB):
    """
    Encuentra el camino de costo mínimo entre un país A (previamente cargado )y un país B.

    Args:
        analyzer
        paisB

    Returns:
        El menor camino entre país A y el país B.
    """
    return model.minimumCostPath(analyzer, paisB)




def mstPRIM(analyzer):
    '''
    Crea el MST de analyzer['landingPoints]
    '''
    return model.mstPRIM(analyzer)
