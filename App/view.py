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
import folium
from branca.element import Figure
import webbrowser



import sys

from numpy import info
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

    return vertice




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

        return path
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

        verticeMasArcosReq2 = printReq2(analyzer, controller.req2(analyzer))  # Lista ordenada
        



    elif int(inputs[0]) == 4:   # Req 3

        paisA = input("\nIngrese el nombre del primer país que desea consultar. Ejemplo: Colombia\n~ ")
        paisB = input("\nIngrese el nombre del segundo país que desea consultar. Ejemplo: Indonesia\n~ ")


        controller.minimumCostPaths(analyzer, paisA)


        pathReq3 = printReq3(analyzer, paisB)




    elif int(inputs[0]) == 5:   # Req 4


        resultados = controller.req4(analyzer)
        distanciaMax = controller.bfsReq4(analyzer)
        print(distanciaMax[1])

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

        
        verticeMasArcosReq2 = verticeMasArcosReq2['vertice']
        pais = verticeMasArcosReq2.split('-')[1]

        paisValue = mp.get(analyzer['countries'], pais)['value']

        coordenadasPais = [paisValue['CapitalLatitude'], paisValue['CapitalLongitude']]

        baseReq2 = Figure(width=750, height=550)
        mapaReq2= folium.Map(
            location=coordenadasPais,
            tiles='cartodbpositron',
            zoom_start= 6
        )

        grupoCaminos = folium.FeatureGroup("Req 2")

        for arco in lt.iterator(gr.adjacentEdges(analyzer['landingPoints'], verticeMasArcosReq2)):

            verticeB = arco['vertexB']

            id_verticeB = arco['vertexB'].split('-')[0]

            '''
            {'key': '4862', 'value': {'landing_point_id': '4862', 'id': 'virginia-beach-va-united-states', 'name': 'Virginia Beach, VA, United States', 'latitude': 36.755008, 'longitude': -76.059198, 
            'lista': {'elements': ['4862-BRUSA', '4862-BRUSA', '4862-Confluence-1', '4862-Confluence-1', '4862-Confluence-1', '4862-Confluence-1', '4862-Dunant', '4862-Dunant', '4862-MAREA', '4862-MAREA'], 'size': 10, 'type': 'ARRAY_LIST', 'cmpfunction': <function defaultfunction at 0x000001DC70E5EE58>, 'key': None}}}
            '''

            infoVerticeB = mp.get(analyzer['infoLandingPoints'], id_verticeB)

            if infoVerticeB is not None:
                coordenadas = [infoVerticeB['value']['latitude'], infoVerticeB['value']['longitude']]

                markerB = folium.Marker(coordenadas, popup="{0}".format(verticeB))

                markerB.add_to(mapaReq2)

                total = [
                    coordenadasPais,
                    coordenadas
                ]

                caminoB = folium.vector_layers.PolyLine(total, popup="{0} => {1}".format(verticeMasArcosReq2, verticeB), color='purple',weight=1)

                caminoB.add_to(grupoCaminos)

            
        grupoCaminos.add_to(mapaReq2)
        folium.LayerControl().add_to(mapaReq2)
        

        baseReq2.add_child(mapaReq2)

        mapaReq2.save("REQ2.html")

        url = "C:\\Users\\juanj\\OneDrive\\Desktop\\Reto 4\\Reto4-G06\\REQ2.html"
        nuevo=2
        webbrowser.open(url, new=nuevo)



        """
        REQ 3 
        """



        baseReq3 = Figure(width=750, height=550)
        mapaReq3= folium.Map(
            location=[0,0],
            tiles='cartodbpositron',
            zoom_start= 3
        )

        grupoCaminos3 = folium.FeatureGroup("Req 3")

        # (pathReq3) Linked List

        for arco in lt.iterator(pathReq3):

            #{'vertexA': 'Bogota-Colombia', 'vertexB': '5808-Maya-1', 'weight': 568.2484982771667}

            if arco['vertexA'][0] not in '1234567890':

                pais = arco['vertexA'].split('-')[1]
                paisValue = mp.get(analyzer['countries'], pais)['value']

                coordenadasA = [paisValue['CapitalLatitude'], paisValue['CapitalLongitude']]
            else:
                id_verticeA = arco['vertexA'].split('-')[0]
                infoVerticeA = mp.get(analyzer['infoLandingPoints'], id_verticeA)

                if infoVerticeA is not None:
                    coordenadasA = [infoVerticeA['value']['latitude'], infoVerticeA['value']['longitude']]
            markerA = folium.Marker(coordenadasA, popup=arco['vertexA'])
            markerA.add_to(mapaReq3)
            if arco['vertexB'][0] not in '1234567890':

                pais = arco['vertexB'].split('-')[1]
                paisValue = mp.get(analyzer['countries'], pais)['value']

                coordenadasB = [paisValue['CapitalLatitude'], paisValue['CapitalLongitude']]
            else:
                id_verticeB = arco['vertexB'].split('-')[0]
                infoVerticeB = mp.get(analyzer['infoLandingPoints'], id_verticeB)

                if infoVerticeB is not None:
                    coordenadasB = [infoVerticeB['value']['latitude'], infoVerticeB['value']['longitude']]

            markerB = folium.Marker(coordenadasB, popup=arco['vertexB'])
            markerB.add_to(mapaReq3)
            camino = folium.vector_layers.PolyLine([coordenadasA, coordenadasB], popup="{0} => {1}".format(arco['vertexA'], arco['vertexB']), color='green', weight=2)

            camino.add_to(grupoCaminos3)

        grupoCaminos3.add_to(mapaReq3)
        folium.LayerControl().add_to(mapaReq3)

        baseReq3.add_child(mapaReq3)
        
        mapaReq3.save("REQ3.html")

        url3 = "C:\\Users\\juanj\\OneDrive\\Desktop\\Reto 4\\Reto4-G06\\REQ3.html"
        nuevo=2
        webbrowser.open(url3, new=nuevo)



        """ 
        REQ 4
        """
        """
        {'first': {'info': 'Bogota-Colombia', 'next': {'info': '4315-South America-1 (SAm-1)', 'next': 
            {'info': '5800-South America-1 (SAm-1)', 'next': {'info': 'Santiago-Chile', 'next': {'info': '16012-Segunda FOS Canal de Chacao', 'next': {'info': 'Beijing-China', 'next': {'info': '6007-Asia Africa Europe-1 (AAE-1)', 'next': {'info': '5723-Asia Africa Europe-1 (AAE-1)', 'next': {'info': '5723-MedNautilus Submarine System', 'next': {'info': '3905-MedNautilus Submarine System', 'next': {'info': '3221-MedNautilus Submarine System', 'next': {'info': '3221-KAFOS', 'next': {'info': '6059-KAFOS', 'next': {'info': '5356-KAFOS', 'next': None}}}}}}}}}}}}}}, 'last': {'info': '5356-KAFOS', 'next': None},
         'size': 14, 'key': None, 'type': 'SINGLE_LINKED', 'cmpfunction': <function defaultfunction at 0x000001C1A4847B88>}
        """

        baseReq4 = Figure(width=750, height=550)
        mapaReq4= folium.Map(
            location=[0,0],
            tiles='cartodbpositron',
            zoom_start= 3
        )

        grupoCaminos4 = folium.FeatureGroup("Req 4")


        distanciaMax = distanciaMax[1] # Es el path y un linked list

        coordREQ3 = []

        for vertice in lt.iterator(distanciaMax):

            if vertice[0] not in "1234567890":

                pais = vertice.split("-")[1]
                paisValue = mp.get(analyzer['countries'], pais)['value']

                coordenadasA = [paisValue['CapitalLatitude'], paisValue['CapitalLongitude']]

                marker3 = folium.Marker(coordenadasA, popup=vertice)
                marker3.add_to(mapaReq4)
                coordREQ3.append(coordenadasA)

            else:
                id_vertice = vertice.split('-')[0]
                infoVertice = mp.get(analyzer['infoLandingPoints'], id_vertice)

                if infoVertice is not None:
                    coordenadasA = [infoVertice['value']['latitude'], infoVertice['value']['longitude']]

                    marker3 = folium.Marker(coordenadasA, popup=vertice)
                    marker3.add_to(mapaReq4)
                    coordREQ3.append(coordenadasA)
        caminoREQ4 = folium.vector_layers.PolyLine(coordREQ3, color='red', weight=2)
        caminoREQ4.add_to(grupoCaminos4)

        grupoCaminos4.add_to(mapaReq4)
        folium.LayerControl().add_to(mapaReq4)

        baseReq4.add_child(mapaReq4)
        mapaReq4.save("REQ4.html")

        url4 = "C:\\Users\\juanj\\OneDrive\\Desktop\\Reto 4\\Reto4-G06\\REQ4.html"
        nuevo=2
        webbrowser.open(url4, new=nuevo)


        
    else:
        sys.exit(0)
sys.exit(0)
