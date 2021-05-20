"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import controller
from DISClib.ADT import list as lt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as mp
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""


def printMenu():
    print("\nBienvenido")
    print("1- Cargar información en el catálogo")
    print("2- REQ 1: Identificar los clústeres de comunicación")
    print("3- REQ 2: Identificar los puntos de conexión críticos de la red")
    print("4- REQ 3: La ruta de menor distancia")
    print("5- REQ 4: Identificar la Infraestructura Crítica de la Red")
    print("6- REQ 5: Análisis de fallas")
    print("7- REQ 6: Los mejores canales para transmitir")
    print("8- REQ 7: La mejor ruta paracomunicarme")
    print("9- REQ 8: REQ. 8: Graficando los Grafos")


analyzer = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")
        analyzer = controller.init()

        # Carga de Datos
        resultado = controller.loadLandingPoints(analyzer)
        loadConnections = controller.loadConnectionsCSV(analyzer)
        pais = controller.loadCountries(analyzer)['value']

        # Prints

        print(f"\nTotal de landing points: {gr.numVertices(analyzer['landingPoints'])}")
        print(f"\nTotal de conexiones: {gr.numEdges(analyzer['landingPoints'])}")
        print(f"\nTotal de paises: {mp.size(analyzer['countries'])}")
        print("\nPrimer landing point cargado: ID: {0}, Nombre: {1}, Latitud: {2}, Longitud: {3}".format(loadConnections["cable_id"], loadConnections["cable_name"], resultado[0], resultado[1]))
        print("\nÚtilmo país cargado: Nombre: {0}, Población: {1}, Número de habitantes: {2}".format(pais["CountryName"], pais["Population"], pais["Internet users"]))
        #TODO: Los dos prints
        # print("Info. del último país cargado:\nNombre: {0} Población: {1} Usuarios de Internet: {2}".format(ultimoCountry['CountryName'], ultimoCountry['Population'], ultimoCountry['Internet users']))


    elif int(inputs[0]) == 2:
        pass

    elif int(inputs[0]) == 3:
        pass

    elif int(inputs[0]) == 4:
        pass

    elif int(inputs[0]) == 5:
        pass

    elif int(inputs[0]) == 6:
        pass

    elif int(inputs[0]) == 7:
        pass

    elif int(inputs[0]) == 8:
        pass

    elif int(inputs[0]) == 9:
        pass

    else:
        sys.exit(0)
sys.exit(0)
