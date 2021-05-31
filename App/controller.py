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
            #model.addCapacityTBPSConnection(analyzer, filtered_dict)

    return first




def loadCountries(analyzer):
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
            model.addCapitalLandingPointTBPS(analyzer, filtered_dict)

    resultado = model.lastCountry(analyzer, analyzer['orderedCountries'])
    analyzer['orderedCountries'] = None # Somos fancy y nos gusta el espacio en memoria
    return resultado





def loadLandingPoints(analyzer):
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




def loadTBPSRepetidos(analyzer):

    model.loadTBPSRepetidos(analyzer)
# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo



def connectedComponents(analyzer)->int:
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    return model.connectedComponents(analyzer=analyzer)



def requerimiento1(analyzer, vertexA:str, vertexB:str):

    return model.requerimiento1(analyzer, vertexA, vertexB)



def req2(analyzer):
    '''
    Retorna una lista ordenada según la cantidad de arcos de cada vértice.
    '''
    return model.req2(analyzer)


def req4(analyzer):
    return model.req4(analyzer)


def bfsReq4(analyzer):
    return model.bfsReq4(analyzer)


def minimumCostPaths(analyzer, paisA):

    return model.minimumCostPaths(analyzer, paisA)



def hasPath(analyzer, paisB):

    return model.hasPath(analyzer, paisB)



def minimumCostPath(analyzer, paisB):
    return model.minimumCostPath(analyzer, paisB)



def mstPRIM(analyzer):
    '''
    Crea el MST de analyzer['landingPoints]
    '''
    return model.mstPRIM(analyzer)
