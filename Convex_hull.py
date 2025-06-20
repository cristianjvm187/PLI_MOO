import numpy as np
import matplotlib.pyplot as plt  # Para visualización


def convex_hull_andrew(puntos):
    """
    Calcula el Convex Hull usando el algoritmo de Cadena Monótona de Andrew,
    optimizado para trabajar con arrays de NumPy.

    Parámetros:
    puntos -- Array de NumPy de shape (n, 2) donde cada fila es un punto (x, y)

    Retorna:
    Array de NumPy con los puntos del convex hull en orden clockwise
    """
    # Paso 1: Ordenar los puntos lexicográficamente
    puntos_ordenados = puntos[np.lexsort((puntos[:, 1], puntos[:, 0]))]

    n = len(puntos_ordenados)
    # Casos triviales
    if n <= 1:
        return puntos_ordenados

    # Paso 2: Construir la cadena inferior
    lower = []
    for i in range(n):
        while len(lower) >= 2 and not es_giro_izquierdo_np(
            lower[-2], lower[-1], puntos_ordenados[i]
        ):
            lower.pop()
        lower.append(puntos_ordenados[i])

    # Paso 3: Construir la cadena superior
    upper = []
    for i in range(n - 1, -1, -1):
        while len(upper) >= 2 and not es_giro_izquierdo_np(
            upper[-2], upper[-1], puntos_ordenados[i]
        ):
            upper.pop()
        upper.append(puntos_ordenados[i])

    # Paso 4: Combinar ambas cadenas (sin duplicar los puntos extremos)
    convex_hull = np.vstack([np.array(lower[:-1]), np.array(upper[:-1])])

    return convex_hull


def es_giro_izquierdo_np(a, b, c):
    """
    Versión optimizada con NumPy para calcular la orientación de tres puntos.

    Parámetros:
    a, b, c -- Arrays de NumPy de shape (2,) representando puntos (x, y)

    Retorna:
    True si es un giro a la izquierda (counter-clockwise), False en caso contrario
    """
    # Calcula el determinante (producto cruz en 2D)
    det = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return det > 0


# Función auxiliar para visualización
def plot_convex_hull_np(puntos, hull):
    """Visualiza los puntos y el convex hull usando NumPy arrays"""
    plt.figure(figsize=(8, 6))
    plt.scatter(puntos[:, 0], puntos[:, 1], color="blue", label="Puntos")

    if len(hull) > 0:
        # Cerramos el polígono conectando el último punto con el primero
        hull_closed = np.vstack([hull, hull[0]])
        plt.plot(hull_closed[:, 0], hull_closed[:, 1], "r-", label="Convex Hull")

    plt.legend()
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Convex Hull - Algoritmo de Andrew (NumPy)")
    plt.grid(True)
    plt.show()


def distancia_minima_al_origen(hull):
    """
    Calcula la distancia mínima desde el origen (0,0) al convex hull.
    Si el origen está dentro del convex hull, retorna 0.

    Parámetros:
    hull -- Array de NumPy de shape (m, 2) con los puntos del convex hull en orden clockwise

    Retorna:
    distancia mínima al origen
    """
    origen = np.array([0.0, 0.0])

    # Caso 1: Si el hull está vacío o el origen es uno de los puntos
    if len(hull) == 0:
        return 0.0
    if any(np.all(p == origen) for p in hull):
        return 0.0

    # Caso 2: Verificar si el origen está dentro del convex hull
    if punto_dentro_poligono_convexo(origen, hull):
        return 0.0

    # Caso 3: Calcular distancia mínima a todas las aristas
    distancias = []
    n = len(hull)

    for i in range(n):
        p1 = hull[i]
        p2 = hull[(i + 1) % n]  # Siguiente punto (conexión circular)

        # Calcular distancia del origen al segmento p1-p2
        dist = distancia_punto_segmento(origen, p1, p2)
        distancias.append(dist)

    return min(distancias)


def punto_dentro_poligono_convexo(punto, hull):
    """
    Determina si un punto está dentro de un polígono convexo.

    Parámetros:
    punto -- Array de shape (2,) con coordenadas (x,y)
    hull -- Array de shape (m, 2) con los puntos del convex hull en orden clockwise

    Retorna:
    True si el punto está dentro, False si está fuera
    """
    n = len(hull)
    if n < 3:
        return False

    # Verificar que todos los productos cruz tengan el mismo signo
    signos = []
    for i in range(n):
        p1 = hull[i]
        p2 = hull[(i + 1) % n]
        cross = (p2[0] - p1[0]) * (punto[1] - p1[1]) - (p2[1] - p1[1]) * (
            punto[0] - p1[0]
        )
        if np.isclose(cross, 0):  # Punto en el borde
            continue
        signos.append(np.sign(cross))

    # Si todos los signos son iguales (considerando bordes), está dentro
    if len(set(signos)) <= 1:
        return True
    return False


def distancia_punto_segmento(p, a, b):
    """
    Calcula la distancia mínima entre un punto p y un segmento de recta ab.

    Parámetros:
    p -- Punto (array de shape (2,))
    a, b -- Extremos del segmento (arrays de shape (2,))

    Retorna:
    Distancia mínima
    """
    # Vector ab
    ab = b - a
    # Vector ap
    ap = p - a

    # Proyección escalar de ap sobre ab
    t = np.dot(ap, ab) / np.dot(ab, ab)

    # Si la proyección está fuera del segmento
    if t <= 0.0:
        return np.linalg.norm(ap)  # Distancia a a
    elif t >= 1.0:
        return np.linalg.norm(p - b)  # Distancia a b
    else:
        # Punto más cercano está en el segmento
        punto_proyeccion = a + t * ab
        return np.linalg.norm(p - punto_proyeccion)


def punto_distancia_minima_al_origen(hull):
    """
    Encuentra el punto más cercano al origen (0,0) en el convex hull.
    Si el origen está dentro del convex hull, retorna (0,0) y distancia 0.

    Parámetros:
    hull -- Array de NumPy de shape (m, 2) con los puntos del convex hull en orden clockwise

    Retorna:
    (punto_mas_cercano, distancia_minima)
    """
    origen = np.array([0.0, 0.0])

    # Caso 1: Si el hull está vacío
    if len(hull) == 0:
        return (origen, 0.0)

    # Caso 2: Si el origen es uno de los puntos del hull
    for p in hull:
        if np.allclose(p, origen):
            return (origen, 0.0)

    # Caso 3: Verificar si el origen está dentro del convex hull
    if punto_dentro_poligono_convexo(origen, hull):
        return (origen, 0.0)

    # Caso 4: Calcular distancia mínima a todas las aristas
    distancia_min = float("inf")
    punto_cercano = None

    n = len(hull)
    for i in range(n):
        p1 = hull[i]
        p2 = hull[(i + 1) % n]  # Siguiente punto (conexión circular)

        # Calcular punto más cercano y distancia al segmento p1-p2
        punto, dist = punto_mas_cercano_segmento(origen, p1, p2)

        if dist < distancia_min:
            distancia_min = dist
            punto_cercano = punto

    return (punto_cercano, distancia_min)


def punto_mas_cercano_segmento(p, a, b):
    """
    Encuentra el punto más cercano en el segmento ab al punto p.

    Parámetros:
    p -- Punto (array de shape (2,))
    a, b -- Extremos del segmento (arrays de shape (2,))

    Retorna:
    (punto_mas_cercano, distancia)
    """
    # Vector ab
    ab = b - a
    # Vector ap
    ap = p - a

    # Proyección escalar de ap sobre ab
    t = np.dot(ap, ab) / np.dot(ab, ab)

    # Clampear t al rango [0, 1] para quedarnos en el segmento
    t = np.clip(t, 0.0, 1.0)

    # Punto más cercano en el segmento
    punto_cercano = a + t * ab
    distancia = np.linalg.norm(p - punto_cercano)

    return (punto_cercano, distancia)


# (Las funciones convex_hull_andrew y punto_dentro_poligono_convexo permanecen iguales que antes)

# Ejemplo completo de uso
if __name__ == "__main__":
    # Generar puntos aleatorios
    np.random.seed(42)
    puntos = np.random.rand(20, 2) * 10 - 3  # Puntos entre -3 y 7

    # Calcular convex hull
    hull = convex_hull_andrew(puntos)

    # Encontrar punto más cercano y distancia
    punto_cercano, distancia = punto_distancia_minima_al_origen(hull)

    print(f"Punto más cercano al origen: {punto_cercano}")
    print(f"Distancia mínima: {distancia:.4f}")

    # Visualización
    plt.figure(figsize=(8, 8))

    # Dibujar puntos
    plt.scatter(puntos[:, 0], puntos[:, 1], color="blue", label="Puntos")
    plt.scatter(0, 0, color="red", s=100, label="Origen")

    # Dibujar convex hull
    if len(hull) > 0:
        hull_cerrado = np.vstack([hull, hull[0]])
        plt.plot(hull_cerrado[:, 0], hull_cerrado[:, 1], "r-", label="Convex Hull")

    # Dibujar punto más cercano y línea de distancia
    if distancia > 0:
        plt.scatter(
            [punto_cercano[0]],
            [punto_cercano[1]],
            color="green",
            s=100,
            label="Punto más cercano",
        )
        plt.plot(
            [0, punto_cercano[0]],
            [0, punto_cercano[1]],
            "g--",
            label=f"Distancia: {distancia:.2f}",
        )

    plt.title("Punto más cercano al origen en Convex Hull")
    plt.legend()
    plt.grid(True)
    plt.axhline(0, color="black", linewidth=0.5)
    plt.axvline(0, color="black", linewidth=0.5)

    plt.show()
