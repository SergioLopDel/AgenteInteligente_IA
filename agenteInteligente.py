import pygame
import random
import time
import math

# Inicializar pygame
pygame.init()

# Definir el tamaño del mapa
tamano = 10  # Reducido para visualizar mejor en pantalla
tamano_celda = 50  # Tamaño de cada celda en píxeles
tamano_ventana = tamano * tamano_celda

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Cargar imágenes
img_agente = pygame.image.load("assets/avatar.png")
img_wumpus = pygame.image.load("assets/wumpus.jpg")
img_pozo = pygame.image.load("assets/tree1.png")
img_premio = pygame.image.load("assets/treasure.png")
img_pasto = pygame.image.load("assets/grass2.jpg")
img_camino = pygame.image.load("assets/road.jpg")

# Redimensionar imágenes
img_agente = pygame.transform.scale(img_agente, (tamano_celda, tamano_celda))
img_wumpus = pygame.transform.scale(img_wumpus, (tamano_celda, tamano_celda))
img_pozo = pygame.transform.scale(img_pozo, (tamano_celda, tamano_celda))
img_premio = pygame.transform.scale(img_premio, (tamano_celda, tamano_celda))
img_pasto = pygame.transform.scale(img_pasto, (tamano_celda, tamano_celda))
img_camino = pygame.transform.scale(img_camino, (tamano_celda, tamano_celda))

# Configurar la pantalla
pantalla = pygame.display.set_mode((tamano_ventana, tamano_ventana))
pygame.display.set_caption("Proyecto 1.- Agente Inteligente")

# Clase del tablero
class Tablero:
    def __init__(self, tamano):
        self.tamano = tamano
        self.mapa = [['' for _ in range(tamano)] for _ in range(tamano)]
        self.costos = [[1 for _ in range(tamano)] for _ in range(tamano)]  # Costos iniciales
        self.peligros = []
        self.premio = []
        self.monstruo = []
        self.revelado = [[False for _ in range(tamano)] for _ in range(tamano)]  # Para mostrar costos
        self.crearMundo()

    def crearMundo(self):
        # Asegurarse de que la posición (0, 0) esté libre
        while True:
            # Se coloca el wumpus en una celda aleatoria
            self.monstruo = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
            self.mapa[self.monstruo[0]][self.monstruo[1]] = "W"

            # Se colocan los obstáculos (número de pozos)
            self.peligros = []
            for _ in range(5):  # Reducimos el número de pozos
                pozo = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
                while pozo == self.monstruo or pozo in self.peligros:  # Evitar que se repitan las posiciones
                    pozo = (random.randint(0, self.tamano - 1), (random.randint(0, self.tamano - 1)))
                self.peligros.append(pozo)
                self.mapa[pozo[0]][pozo[1]] = 'P'

            # Se coloca el premio en el mapa
            self.premio = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
            while self.premio == self.monstruo or self.premio in self.peligros:
                self.premio = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
            self.mapa[self.premio[0]][self.premio[1]] = "F"

            # Asignar costos a las celdas
            for i in range(self.tamano):
                for j in range(self.tamano):
                    if self.mapa[i][j] == '':  # Celda vacía
                        # Asignar costos aleatorios: 1 (normal), 2 (terreno A), 3 (terreno B)
                        self.costos[i][j] = random.choice([1, 2, 3])

            # Verificar que la posición (0, 0) esté libre
            if (0, 0) not in self.peligros and (0, 0) != self.monstruo and (0, 0) != self.premio:
                break
            else:
                # Si no está libre, reiniciar el mundo
                self.mapa = [['' for _ in range(self.tamano)] for _ in range(self.tamano)]
                self.costos = [[1 for _ in range(self.tamano)] for _ in range(self.tamano)]
                self.peligros = []
                self.premio = []
                self.monstruo = []
                self.revelado = [[False for _ in range(self.tamano)] for _ in range(self.tamano)]

    def dibujar(self, agente_pos):
        pantalla.fill(BLANCO)
        for i in range(self.tamano):
            for j in range(self.tamano):
                x, y = j * tamano_celda, i * tamano_celda
                pantalla.blit(img_pasto, (x, y))
                if (i, j) in self.peligros:
                    pantalla.blit(img_pozo, (x, y))
                elif (i, j) == self.monstruo:
                    pantalla.blit(img_wumpus, (x, y))
                elif (i, j) == self.premio:
                    pantalla.blit(img_premio, (x, y))
                elif (i, j) == agente_pos:
                    pantalla.blit(img_agente, (x, y))
        pygame.display.flip()

# Clase para representar un nodo en el mundo
class Nodo:
    def __init__(self, posicion, padre=None):
        self.posicion = posicion
        self.padre = padre
        self.g = 0  # Costo desde el inicio hasta este nodo
        self.h = 0  # Heurística (estimación del costo hasta el premio)
        self.f = 0  # Costo total (g + h)

    def __eq__(self, otro):
        return self.posicion == otro.posicion

    def __repr__(self):
        return f"{self.posicion} (g={self.g}, h={self.h}, f={self.f})"

# Agente Inteligente
class Agente:
    def __init__(self, mundo):
        self.mundo = mundo
        self.posicion = (0, 0)  # Comienza en la esquina superior izquierda
        self.vivo = True
        self.oro_recogido = False
        self.ruta = []  # Para almacenar la ruta completa
        self.costo_total = 0  # Para almacenar el costo total de la ruta

    def distancia_manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_estrella(self):
        # Inicializar nodo inicial y nodo objetivo
        nodo_inicio = Nodo(self.posicion)
        nodo_objetivo = Nodo(self.mundo.premio)

        # Listas abierta y cerrada
        abierta = []
        cerrada = set()

        # Agregar el nodo inicial a la lista abierta
        abierta.append(nodo_inicio)

        while abierta:
            # Obtener el nodo con el menor costo f
            nodo_actual = min(abierta, key=lambda n: n.f)
            abierta.remove(nodo_actual)
            cerrada.add(nodo_actual.posicion)

            # Verificar si hemos llegado al objetivo
            if nodo_actual == nodo_objetivo:
                return self.reconstruir_ruta(nodo_actual)

            # Generar nodos hijos
            for movimiento in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nueva_pos = (nodo_actual.posicion[0] + movimiento[0], nodo_actual.posicion[1] + movimiento[1])

                # Verificar si la nueva posición es válida
                if 0 <= nueva_pos[0] < self.mundo.tamano and 0 <= nueva_pos[1] < self.mundo.tamano:
                    # Verificar si la nueva posición es un peligro
                    if nueva_pos in self.mundo.peligros or nueva_pos == self.mundo.monstruo:
                        continue

                    # Crear un nuevo nodo
                    nodo_hijo = Nodo(nueva_pos, nodo_actual)

                    # Si el nodo ya está en la lista cerrada, ignorarlo
                    if nodo_hijo.posicion in cerrada:
                        continue

                    # Calcular g, h y f
                    costo_movimiento = self.mundo.costos[nueva_pos[0]][nueva_pos[1]]  # Costo de la celda
                    nodo_hijo.g = nodo_actual.g + costo_movimiento
                    nodo_hijo.h = self.distancia_manhattan(nodo_hijo.posicion, nodo_objetivo.posicion)
                    nodo_hijo.f = nodo_hijo.g + nodo_hijo.h

                    # Si el nodo ya está en la lista abierta y tiene un costo mayor, ignorarlo
                    if any(nodo_hijo.posicion == n.posicion and nodo_hijo.g > n.g for n in abierta):
                        continue

                    # Agregar el nodo a la lista abierta
                    abierta.append(nodo_hijo)

        return None  # No se encontró un camino

    def reconstruir_ruta(self, nodo):
        ruta = []
        while nodo:
            ruta.append(nodo.posicion)
            nodo = nodo.padre
        ruta.reverse()
        return ruta

    def mover_hacia_premio(self):
        if not self.vivo or self.oro_recogido:
            return

        # Encontrar el camino usando A*
        ruta = self.a_estrella()
        if not ruta:
            print("No hay camino seguro hacia el premio.")
            return

        # Moverse paso a paso por la ruta
        for paso in ruta:
            self.posicion = paso
            self.ruta.append(self.posicion)  # Agregar la posición actual a la ruta
            self.costo_total += self.mundo.costos[paso[0]][paso[1]]  # Sumar el costo de la celda
            self.mundo.revelado[paso[0]][paso[1]] = True  # Revelar el costo de la celda
            self.percepcion()
            self.mundo.dibujar(self.posicion)
            print(f"Ruta actual: {self.ruta}")  # Mostrar la ruta actual
            time.sleep(1)

            if not self.vivo or self.oro_recogido:
                break

        # Mostrar la ruta completa y el costo total al final
        if self.oro_recogido:
            print("\n¡Ruta completa encontrada!")
            print(" -> ".join(map(str, self.ruta)))
            print(f"Costo total de la ruta: {self.costo_total}")

    def percepcion(self):
        x, y = self.posicion
        # Ver si el agente ha caído en un pozo
        if self.posicion in self.mundo.peligros:
            print("¡Has caído en un pozo! Estás muerto.")
            self.vivo = False
            return

        # Ver si el agente está cerca del Wumpus
        if abs(x - self.mundo.monstruo[0]) <= 1 and abs(y - self.mundo.monstruo[1]) <= 1:
            print("Sientes el olor del Wumpus... ¡Cuidado!")
        
        # Ver si el agente ha encontrado el oro
        if self.posicion == self.mundo.premio:
            print("¡Has encontrado el oro!")
            self.oro_recogido = True

        # Ver si el agente ha llegado al Wumpus
        if self.posicion == self.mundo.monstruo:
            print("¡Has sido devorado por el Wumpus! Estás muerto.")
            self.vivo = False

    def estado(self):
        if self.vivo:
            print(f"Posición actual: {self.posicion}")
        else:
            print("El agente ha muerto.")

# Crear mundo y agente
mundo = Tablero(tamano)  # Crear el mundo
agente = Agente(mundo)  # Crear el agente

# Dibujar el estado inicial
mundo.dibujar(agente.posicion)
time.sleep(2)

# El agente intenta moverse hacia el premio
agente.mover_hacia_premio()

# Mantener la ventana abierta hasta que el usuario la cierre
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
