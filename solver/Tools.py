import matplotlib.pyplot as plt
import numpy as np
import random


def l1(x: np.ndarray, y: np.ndarray):
    return np.linalg.norm(x - y, ord=1)


def l2(x: np.ndarray, y: np.ndarray):
    return np.linalg.norm(x - y)


def colinear(x: np.ndarray, y: np.ndarray):
    if (x[0] * y[1] - x[1] * y[0]) == 0:
        return True
    return False


def sgn(x):
    if x >= 0:
        return 1
    return -1


def projection(x: np.ndarray, a, b, c, d):
    comp_x = x[0]
    comp_y = x[1]
    comp_x = min(max(comp_x, a), b)
    comp_y = min(max(comp_y, c), d)
    return np.array([comp_x, comp_y])


def inicial_point(a, b, c, d):
    x = [random.uniform(a, b), random.uniform(c, d)]
    # print(x)
    return x


def len_skip(p0, v, a, b, c, d):
    x0 = p0[0]
    y0 = p0[1]
    vx = v[0]
    vy = v[1]
    intersecciones = []

    # x = a
    if abs(vx) > 1e-5:
        t = (a - x0) / vx
        y = y0 + t * vy
        if t > 0 and (y - c >= 0) and d - y >= 0:
            intersecciones.append(t)

    # x = b
    if abs(vx) > 1e-5:
        t = (b - x0) / vx
        y = y0 + t * vy

        if t > 0 and (y - c >= 0) and d - y >= 0:
            intersecciones.append(t)
            # raise ValueError(len(intersecciones), intersecciones, p0)
    # y = c
    if abs(vy) > 1e-5:
        t = (c - y0) / vy
        x = x0 + t * vx

        if t > 0 and x - a >= 0 and b - x >= 0:
            intersecciones.append(t)

    # y = d
    if abs(vy) > 1e-5:
        t = (d - y0) / vy
        x = x0 + t * vx
        if t > 0 and x - a >= 0 and b - x >= 0:
            intersecciones.append(t)

    if len(intersecciones) == 0:
        #    return None  # No hay intersección en esa dirección
        raise ValueError("mierda", p0, "dime quiene s ", v, a, b, c, d)

    # Devolver la primera intersección
    return min(intersecciones)


def lado_borde(p, a, b, c, d, tol):
    x = p[0]
    y = p[1]
    lados = []
    if abs(x - a) < tol and c <= y <= d:
        lados.append("left")
    if abs(x - b) < tol and c <= y <= d:
        lados.append("right")
    if abs(y - c) < tol and a <= x <= b:
        lados.append("bottom")
    if abs(y - d) < tol and a <= x <= b:
        lados.append("top")
    return lados


def proyectar_direccion(p, dir, a, b, c, d, tol):
    lados = lado_borde(p, a, b, c, d, tol)
    if not lados:
        raise ValueError("El punto no está en el contorno del rectángulo.")

    dir = np.array(dir, dtype=float)
    vx, vy = dir

    # Casos especiales: esquinas
    esquina = None
    if "left" in lados and "bottom" in lados:
        esquina = "inf_izq"
    elif "right" in lados and "bottom" in lados:
        esquina = "inf_der"
    elif "right" in lados and "top" in lados:
        esquina = "sup_der"
    elif "left" in lados and "top" in lados:
        esquina = "sup_izq"

    if esquina:
        # Comportamiento en esquinas
        if esquina == "inf_izq":
            if esta_entre(dir, np.array([1, 0]), np.array([0, 1])):
                return dir
            else:
                # Arreglar este caso con la region
                if abs(vx + 1) < tol and abs(vy + 1) < tol:
                    return np.array([0, 0])
                elif abs(vx) > abs(vy):
                    return np.array([1, 0])
                else:
                    return np.array([0, 1])

        if esquina == "inf_der":
            if esta_entre(dir, np.array([0, 1]), np.array([0, -1])):
                return dir
            else:
                if abs(vx + 1) < tol and abs(vy - 1) < tol:
                    return np.array([0, 0])
                elif abs(vx) > abs(vy):
                    return np.array([-1, 0])
                else:
                    return np.array([0, 1])

        if esquina == "sup_der":
            if esta_entre(dir, np.array([-1, 0]), np.array([0, -1])):
                return dir
            else:
                if abs(vx - 1) < tol and abs(vy - 1) < tol:
                    return np.array([0, 0])
                elif abs(vy) > abs(vx):
                    return np.array([-1, 0])
                else:
                    return np.array([0, -1])

        if esquina == "sup_izq":
            if esta_entre(dir, np.array([0, -1]), np.array([1, 0])):
                return dir
            else:
                if abs(vx + 1) <= 0 and abs(vy - 1) >= 0:
                    return np.array([0, 0])
                elif abs(vy) > abs(vx):
                    return np.array([1, 0])
                else:
                    return np.array([0, -1])
    else:
        # No estamos en una esquina → proyectamos sobre borde directamente
        tangentes = {
            "left": np.array([0, 1]),
            "right": np.array([0, 1]),
            "bottom": np.array([1, 0]),
            "top": np.array([1, 0]),
        }
        for lado in lados:
            t = tangentes[lado]
            proy = np.dot(dir, t) * t
            return proy  # solo un lado, porque no es esquina

    return np.array([0, 0])  # fallback


def esta_entre(v, a, b, incluir_bordes=True):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    # Proyecciones de v sobre a y b
    pa = np.dot(v, a)
    pb = np.dot(v, b)

    if incluir_bordes:
        return pa >= 0 and pb >= 0
    else:
        return pa > 0 and pb > 0
