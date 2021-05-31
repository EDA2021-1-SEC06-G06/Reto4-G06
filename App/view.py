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

import sys
import controller
from DISClib.ADT import list as lt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as mp
from DISClib.ADT import stack
from DISClib.Algorithms.Graphs import prim
from DISClib.ADT import queue
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




def printReq2(analyzer, lista_ordenada):

    posicion = 1
    numeros = '0123456789'
    if lt.getElement(lista_ordenada, posicion)['size'] != lt.getElement(lista_ordenada, posicion + 1)['size']:

        vertice = lt.getElement(lista_ordenada, posicion)

        if vertice['vertice'][0] not in numeros:
            pais = vertice['vertice'].split('-')[1]  # llaves son vertice y size
            print("Nombre/ID: {0} | País: {1} | Arcos:{2}\n".format(vertice['vertice'], pais, vertice['size']))

    else:

        while posicion < lt.size(lista_ordenada) and lt.getElement(lista_ordenada, posicion)['size'] == lt.getElement(lista_ordenada, posicion + 1)['size']:

            verticeDict = lt.getElement(lista_ordenada, posicion)  # llaves son vertice y size

            id_unique = ''

            indice = 0

            while verticeDict['vertice'][indice] in numeros:
                id_unique = id_unique + verticeDict['vertice'][indice]
                indice += 1

            pais = mp.get(analyzer['infoLandingPoints'], id_unique)['value']['name'].split(', ')[1]

            print("Nombre: {0} | País: {1} | ID: {2} | Arcos:{3}\n".format(verticeDict['vertice'], pais, id_unique, verticeDict['size']))

            posicion += 1




def printReq3(analyzer, paisB):


    path = controller.minimumCostPath(analyzer, paisB)

    if path is not None:
        distancia = 0
        for relacion in lt.iterator(path):
            print("{0} ==> {1}\tDistancia(km): {2}".format(relacion['vertexA'], relacion['vertexB'], relacion['weight']))
            distancia += relacion['weight']

        pathlen = stack.size(path)
        print(f"El camino es de longitud: {pathlen}")
        print(f"La distancia total de la ruta es: {distancia} km.")
    else:
        print('No existe un camino.')

analyzer = None
sys.setrecursionlimit(1000*1000)

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:    # Construcción analyzer
        print("Cargando información de los archivos ....")
        analyzer = controller.init()

        # Carga de Datos
        resultado = controller.loadLandingPoints(analyzer)
        loadConnections = controller.loadConnectionsCSV(analyzer)
        # controller.loadTBPSRepetidos(analyzer)   # TBPS
        pais = controller.loadCountries(analyzer)['value']


        # Prints

        print(f"\nTotal de landing points: {gr.numVertices(analyzer['landingPoints'])}")
        print(f"\nTotal de conexiones: {gr.numEdges(analyzer['landingPoints'])}")
        print(f"\nTotal de paises: {mp.size(analyzer['countries'])}")
        print("\nPrimer landing point cargado: ID: {0}, Nombre: {1}, Latitud: {2}, Longitud: {3}".format(loadConnections["cable_id"], loadConnections["cable_name"], resultado[0], resultado[1]))
        print("\nÚtilmo país cargado: Nombre: {0}, Población: {1}, Número de habitantes: {2}".format(pais["CountryName"], pais["Population"], pais["Internet users"]))

        cantidadConnectedComponents = controller.connectedComponents(analyzer)  # REQ1
        controller.mstPRIM(analyzer)
        controller.loadBFS(analyzer)

    elif int(inputs[0]) == 2:   # Req 1
        print(f"Total de clústeres en el grafo: {cantidadConnectedComponents}")


        vertexA = input("Ingrese el nombre del primer Landing Point(Ej. Redondo Beach):\n~ ")
        vertexB = input("Ingrese el nombre del segundo Landing Point(Ej. Vung Tau):\n~ ")

        if controller.requerimiento1(analyzer, vertexA, vertexB):
            print(f"{vertexA} y {vertexB} SÍ están en el mismo Cluster.")

        else:
            print(f"{vertexA} y {vertexB} NO están en el mismo Cluster.")


    elif int(inputs[0]) == 3:   # Req 2
        printReq2(analyzer, controller.req2(analyzer))  # Lista ordenada


    elif int(inputs[0]) == 4:   # Req 3

        paisA = input("Ingrese el nombre del primer país que desea consultar. Ejemplo: Colombia\n~ ")
        paisB = input("Ingrese el nombre del segundo país que desea consultar. Ejemplo: Indonesia\n~ ")
        controller.minimumCostPaths(analyzer, paisA)

        printReq3(analyzer, paisB)


    elif int(inputs[0]) == 5:   # Req 4
        resultados = controller.req4(analyzer)
        distanciaMax = controller.bfsReq4(analyzer)
        print(f"\nNúmero de nodos conectados en la red de expansión mínima: {resultados[0]}\n")
        print(f"Distancia de la red de expansión mínima: {resultados[1] * 2} km\n")  #Se multiplica x2 puesto que es un grafo dirigido
        print("La rama más larga que hace parte de la red de expansión mínima desde 'Bogotá-Colombia' tiene una longitud de {0} y corresponde al landing point: {1}".format(distanciaMax['distTo'], distanciaMax['edgeTo']))

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
