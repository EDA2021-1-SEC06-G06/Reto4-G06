﻿"""
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
import folium
from branca.element import Figure
import webbrowser



import sys
import controller
from DISClib.ADT import list as lt
from DISClib.ADT.graph import gr
from DISClib.ADT import map as mp
from DISClib.ADT import stack

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
            print("\nNombre/ID: {0} | País: {1} | Arcos:{2}\n".format(vertice['vertice'], pais, vertice['size']))

    else:

        while posicion < lt.size(lista_ordenada) and lt.getElement(lista_ordenada, posicion)['size'] == lt.getElement(lista_ordenada, posicion + 1)['size']:

            verticeDict = lt.getElement(lista_ordenada, posicion)  # llaves son vertice y size

            id_unique = ''

            indice = 0

            while verticeDict['vertice'][indice] in numeros:
                id_unique = id_unique + verticeDict['vertice'][indice]
                indice += 1

            pais = mp.get(analyzer['infoLandingPoints'], id_unique)['value']['name'].split(', ')[1]

            print("\nNombre: {0} | País: {1} | ID: {2} | Arcos:{3}\n".format(verticeDict['vertice'], pais, id_unique, verticeDict['size']))

            posicion += 1




def printReq3(analyzer, paisB):


    path = controller.minimumCostPath(analyzer, paisB)

    if path is not None:
        distancia = 0
        for relacion in lt.iterator(path):
            print("\n{0} ==> {1}\tDistancia(km): {2}".format(relacion['vertexA'], relacion['vertexB'], relacion['weight']))
            distancia += relacion['weight']

        pathlen = stack.size(path)
        print(f"\nEl camino es de longitud: {pathlen}")
        print(f"\nLa distancia total de la ruta es: {distancia} km.")
    else:
        print('\nNo existe un camino.')




def printReq5(sorted_list):

    if lt.size(sorted_list) >= 1:
        print("\nNúmero de países afectados: {0}".format(lt.size(sorted_list)))
        for pais in lt.iterator(sorted_list):

            print("\nPaís: {0}\tDistancia: {1}km".format(pais['nombre'], pais['weight']))
    else:
        print("No se encontraron países directamente conectados.")




def printReq6(analyzer, lista, anchoDeBanda):

    for capitalPais in lt.iterator(lista):

        pais = capitalPais.split('-')[1]

        usuarios = mp.get(analyzer['countries'], pais)['value']['Internet users']
        
        print("\nPaís: {0}\tAncho de banda máximo: {1} Mbps".format(pais, (anchoDeBanda / usuarios) * 1000000))




def printReq4andReq7(list):
    for item in lt.iterator(list):
        if item != None:
            print("=>",item)




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
        print(f"\nTotal de clústeres en el grafo: {cantidadConnectedComponents}")


        vertexA = input("\nIngrese el nombre del primer Landing Point(Ej. Redondo Beach):\n~ ")
        vertexB = input("\nIngrese el nombre del segundo Landing Point(Ej. Vung Tau):\n~ ")


        if controller.requerimiento1(analyzer, vertexA, vertexB):

            print(f"\n{vertexA} y {vertexB} SÍ están en el mismo Cluster.")


        else:
            print(f"\n{vertexA} y {vertexB} NO están en el mismo Cluster.")




    elif int(inputs[0]) == 3:   # Req 2

        printReq2(analyzer, controller.req2(analyzer))  # Lista ordenada




    elif int(inputs[0]) == 4:   # Req 3

        paisA = input("\nIngrese el nombre del primer país que desea consultar. Ejemplo: Colombia\n~ ")
        paisB = input("\nIngrese el nombre del segundo país que desea consultar. Ejemplo: Indonesia\n~ ")


        controller.minimumCostPaths(analyzer, paisA)


        printReq3(analyzer, paisB)




    elif int(inputs[0]) == 5:   # Req 4


        resultados = controller.req4(analyzer)
        distanciaMax = controller.bfsReq4(analyzer)


        print(f"\nNúmero de nodos conectados en la red de expansión mínima: {resultados[0]}\n")
        print(f"Distancia de la red de expansión mínima: {resultados[1]} km\n")
        print("\nLa rama más larga que hace parte de la red de expansión mínima desde 'Bogotá-Colombia' tiene una longitud de {0} y corresponde al landing point: {1}".format(distanciaMax[0]['distTo'], distanciaMax[0]['edgeTo']))
        print("\nEl recorrido desde 'Bogotá-Colombia' hasta {0} es el siguiente:\n".format(distanciaMax[0]['edgeTo']))
        printReq4andReq7(distanciaMax[1])




    elif int(inputs[0]) == 6:  # Req 5
        inputLandingPoint = input("\nIngrese el Landing Point que le interesa. Ejemplo: 5808-San Andres Isla Tolu Submarine Cable (SAIT)\n~ ")


        sorted_list = controller.req5(analyzer, inputLandingPoint)


        printReq5(sorted_list)

      


    elif int(inputs[0]) == 7: ## BONO REQ 6 ##
 
        nombrePais = input("\nIngrese el nombre del país que le interesa (Ejemplo: Cuba):\n~ ")
        nombreCable = input("\nIngrese el nombre del cable que desea (Ejemplo: ALBA-1):\n~ ")

        listaPaises, anchoDeBanda = controller.req6(analyzer, nombrePais, nombreCable)

        printReq6(analyzer, listaPaises, anchoDeBanda)




    elif int(inputs[0]) == 8:
        ip1 = input("\nIngrese la primera dirección de IP. Ejemplo: 8.8.8.8\n~")  # Primera dirección de IP
        ip2 = input("\nIngrese la segunda dirección de IP. Ejemplo: 165.132.67.89\n~")  # Segunda dirección de IP
        resultado = controller.req7(ip1, ip2, analyzer)

        if resultado is not False:
            print("\nExiste un camino entre el landing point más cercano a la dirección IP1: {0} y al landing point más cercano a la dirección IP2 {1}.".format(ip1, ip2))
            print("\nEste camino tiene {0} saltos y la ruta es la siguiente:\n".format(resultado[0]))
            printReq4andReq7(resultado[1])

        else: 
            print("\nNO existe un camino entre el landing point más cercano a la dirección IP1: {0} y al landing point más cercano a la dirección IP2 {1}.".format(ip1, ip2))




    elif int(inputs[0]) == 9:
         ##### REQ 1 #####
        baseReq1 = Figure(width=750, height=550)
        mapaReq1= folium.Map(
            location=[0, 0],
            tiles='cartodbpositron',
            zoom_start=2
        )

        for lp in lt.iterator(gr.edges(analyzer['landingPoints'])):
            
            if lp['vertexA'][0] in '1234567890':
                
                # 8833 {'landing_point_id': '8833', 'id': 'kourou-french-guiana', 'name': 'Kourou, French Guiana', 'latitude': 5.168299, 'longitude': -52.645555, 'lista': {'elements': ['8833-Kanawa', '8833-Kanawa'], 'size': 2, 'type': 'ARRAY_LIST', 'cmpfunction': <function defaultfunction at 0x0000024E3D050048>, 'key': None}}
                id_ld = lp['vertexA'].split('-')[0]
                
                valorLP = mp.get(analyzer['infoLandingPoints'], id_ld)['value']

                coordenadas = [valorLP['latitude'], valorLP['longitude']]
                
                markerLP = folium.Marker(coordenadas, popup="{0}-{1}".format(valorLP['landing_point_id'], valorLP['name']))

                markerLP.add_to(mapaReq1)

            else:

                pais = lp['vertexA'].split('-')[1]

                valorPais = mp.get(analyzer['countries'], pais)
                
                if valorPais is not None:
                    # {'key': 'Barbados', 'value': {'CountryName': 'Barbados', 'CapitalName': 'Bridgetown', 'CapitalLatitude': 13.1, 'CapitalLongitude': -59.616667, 'CountryCode': 'BB', 'ContinentName': 'North America', 'Population': 285719.0, 'Internet users': 233604.0}}

                    coordenadas = [valorPais['value']['CapitalLatitude'], valorPais['value']['CapitalLongitude']]

                    markerCapital = folium.Marker(coordenadas, popup=lp['vertexA'])
                    markerCapital.add_to(mapaReq1)

        baseReq1.add_child(mapaReq1)

        mapaReq1.save("C:\\Users\\juanj\\OneDrive\\Desktop\\Reto 4\\Reto4-G06\\App\\REQ1.html")

        url = "C:\\Users\\juanj\\OneDrive\\Desktop\\Reto 4\\Reto4-G06\\App\\REQ1.html"
        nuevo=2
        webbrowser.open(url, new=nuevo)

        datosCluster = analyzer['connected']['idscc']
        # print(datosCluster)
    else:
        sys.exit(0)
sys.exit(0)
