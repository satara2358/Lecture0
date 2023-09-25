import sys

# Definición de la clase Node que representa un nodo en una estructura de datos
class Node():
    # Constructor de la clase Node
    def __init__(self, state, parent, action):
        # El estado del nodo, que puede representar una configuración o posición
        self.state = state
        # El nodo padre, que es el nodo desde el que se llegó a este nodo
        self.parent = parent
        # La acción que llevó desde el nodo padre a este nodo
        self.action = action



# Definición de la clase StackFrontier, que representa una frontera tipo pila
class StackFrontier():
    # Constructor de la clase, inicializa la frontera como una lista vacía
    def __init__(self):
        self.frontier = []

    # Método para agregar un nodo a la frontera
    def add(self, node):
        self.frontier.append(node)

    # Método para verificar si la frontera contiene un estado específico
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    # Método para verificar si la frontera está vacía
    def empty(self):
        return len(self.frontier) == 0

    # Método para eliminar y devolver el último nodo de la frontera (tipo pila)
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Obtiene el último nodo de la frontera y lo elimina de la lista
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


# Definición de la clase QueueFrontier, que representa una frontera tipo cola
class QueueFrontier(StackFrontier):
    # Método para eliminar y devolver el primer nodo de la frontera (tipo cola)
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Obtiene el primer nodo de la frontera y lo elimina de la lista
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


# Definición de la clase Maze, que representa un laberinto
class Maze():

    def __init__(self, filename):
        # Lee el archivo y establece la altura y el ancho del laberinto
        with open(filename) as f:
            contents = f.read()

        # Valida que haya exactamente un punto de inicio y un punto de destino
        if contents.count("A") != 1:
            raise Exception("El laberinto debe tener exactamente un punto de inicio")
        if contents.count("B") != 1:
            raise Exception("El laberinto debe tener exactamente un punto de destino")

        # Determina la altura y el ancho del laberinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Lleva un seguimiento de las paredes del laberinto
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None



# Método para imprimir el laberinto en la consola
    def print(self):
        # Obtiene la solución del laberinto si está disponible
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    # Si la celda es una pared, imprime un carácter sólido (█)
                    print("█", end="")
                elif (i, j) == self.start:
                    # Si la celda es el punto de inicio, imprime "A"
                    print("A", end="")
                elif (i, j) == self.goal:
                    # Si la celda es el punto de destino, imprime "B"
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    # Si la celda está en la solución, imprime un asterisco (*)
                    print("*", end="")
                else:
                    # Si la celda es libre y no se encuentra en la solución, imprime un espacio en blanco
                    print(" ", end="")
            print()
        print()


# Método para encontrar vecinos válidos desde una ubicación dada
    def neighbors(self, state):
        row, col = state
        # Define las posibles acciones y las ubicaciones correspondientes
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            # Verifica si la ubicación es válida (dentro de los límites del laberinto) y no es una pared
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                # Agrega la acción y la ubicación válida a la lista de resultados
                result.append((action, (r, c)))
        return result


    # Método para encontrar una solución para el laberinto
    def solve(self):
        # Lleva un seguimiento del número de estados explorados
        self.num_explored = 0

        # Inicializa la frontera solo con la posición de inicio
        start = Node(state=self.start, parent=None, action=None)
            ## Para búsqueda en profundidad QueueFrontier() || StackFrontier()
        frontier = QueueFrontier()
        frontier.add(start)

        # Inicializa un conjunto explorado vacío
        self.explored = set()

        # Continúa en un bucle hasta encontrar una solución
        while True:
            # Si la frontera está vacía, no hay un camino hacia la solución
            if frontier.empty():
                raise Exception("no solution")

            # Elige un nodo de la frontera
            node = frontier.remove()
            self.num_explored += 1

            # Si el nodo es el objetivo, hemos encontrado una solución
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Marca el nodo como explorado
            self.explored.add(node.state)

            # Agrega los vecinos a la frontera
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)



# Método para generar una imagen del laberinto
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Crea un lienzo en blanco
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        # Obtiene la solución si está disponible
        solution = self.solution[1] if self.solution is not None else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                # Paredes
                if col:
                    fill = (40, 40, 40)
                # Punto de inicio
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                # Punto de destino
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                # Solución
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)
                # Celdas exploradas
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                # Celda vacía
                else:
                    fill = (237, 240, 252)

                # Dibuja la celda
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        # Guarda la imagen en un archivo
        img.save(filename)



# Comprueba si se proporciona el número correcto de argumentos en la línea de comandos (debe ser 2)
if len(sys.argv) != 2:
    # Si no se proporciona el número correcto de argumentos, muestra un mensaje de uso y sale del programa
    sys.exit("Usage: python maze.py maze.txt")

# Crea una instancia de la clase Maze utilizando el archivo de laberinto especificado como argumento de línea de comandos
m = Maze(sys.argv[1])

# Imprime el laberinto inicial en la consola utilizando el método print de la clase Maze
print("Maze:")
m.print()

# Resuelve el laberinto utilizando el método solve de la clase Maze
print("Solving...")
m.solve()

# Imprime la cantidad de estados explorados (nodos) durante la búsqueda
print("States Explored:", m.num_explored)

# Imprime el laberinto nuevamente, esta vez con la solución resaltada, utilizando el método print de la clase Maze
print("Solution:")
m.print()

# Genera una imagen del laberinto y la guarda en un archivo llamado "maze.png".
# También se especifica que se deben mostrar las celdas exploradas en la imagen.
m.output_image("maze.png", show_explored=True)
