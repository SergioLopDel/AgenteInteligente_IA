import random
import os
import time

# Se define el tamaño del mapa
malla = 10  # Área de Búsqueda de 10 X 10

# Representación del mundo (Matriz)
class Tablero:
    def __init__(self, tamano):
        self.tamano = tamano
        self.mapa = [['' for _ in range(tamano)] for _ in range(tamano)]
        self.peligros = []
        self.premio = []
        self.monstruo = []
        self.crearMundo()

    def crearMundo(self):
        # Se coloca el wumpus en una celda aleatoria
        self.monstruo = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
        self.mapa[self.monstruo[0]][self.monstruo[1]] = "W"

        # Se colocan los obstáculos (número de pozos)
        for _ in range(2):
            pozo = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
            while pozo == self.monstruo or pozo in self.peligros:  # Evitar que se repitan las posiciones
                pozo = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
            self.peligros.append(pozo)
            self.mapa[pozo[0]][pozo[1]] = 'P'

        # Se coloca el premio en el mapa
        self.premio = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
        while self.premio == self.monstruo or self.premio in self.peligros:
            self.premio = (random.randint(0, self.tamano - 1), random.randint(0, self.tamano - 1))
        self.mapa[self.premio[0]][self.premio[1]] = "F"

    def mostrarTablero(self, agente_pos):  # Método para mostrar el mapa
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpiar la pantalla
        for i in range(self.tamano):
            for j in range(self.tamano):
                if (i, j) == agente_pos:  # Mostrar la posición del agente
                    print("A", end=" ")
                else:
                    print(self.mapa[i][j] if self.mapa[i][j] else ".", end=" ")
            print()
        print()

# Agente Inteligente
class Agente:
    def __init__(self, mundo):
        self.mundo = mundo
        self.posicion = (0, 0)  # Comienza en la esquina superior izquierda
        self.vivo = True
        self.oro_recogido = False

    def mover_hacia_premio(self):
        if not self.vivo:
            return

        x, y = self.posicion
        premio_x, premio_y = self.mundo.premio

        # Mover hacia el premio
        if x < premio_x:
            self.posicion = (x + 1, y)
        elif x > premio_x:
            self.posicion = (x - 1, y)
        elif y < premio_y:
            self.posicion = (x, y + 1)
        elif y > premio_y:
            self.posicion = (x, y - 1)

        self.percepcion()
        self.mundo.mostrarTablero(self.posicion)  # Mostrar el tablero actualizado
        time.sleep(1)  # Pequeño retraso para ver el movimiento

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
            print("¡Has encontrado el premio!")
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
mundo = Tablero(malla)  # Crear el mundo
agente = Agente(mundo)  # Crear el agente

# Mostrar el mapa inicial
mundo.mostrarTablero(agente.posicion)

# El agente intenta moverse hacia el premio
while agente.vivo and not agente.oro_recogido:
    agente.mover_hacia_premio()

# Mostrar el estado final del agente
agente.estado()