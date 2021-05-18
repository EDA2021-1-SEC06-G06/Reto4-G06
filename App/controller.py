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

        model.addLandingPointConnection(analyzer, filtered_dict)

    return analyzer




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
      
    return analyzer




def loadLandingPoints(analyzer):
    landingPointsFile = cf.data_dir + 'landing_points.csv'

    input_file = csv.DictReader(open(landingPointsFile, encoding='utf-8-sig'), delimiter=',')

    for landingPoint in input_file:
        # landing_point_id,id,name,latitude,longitude
        filtered = {
            'landing_point_id': landingPoint['landing_point_id'],
            'id': landingPoint['id'],
            'name': landingPoint['name'],
            'latitude': float(landingPoint['latitude']),
            'longitude': float(landingPoint['longitude'])
        }
        
        model.addMapLandingPoint(analyzer, filtered)
    return analyzer
# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
