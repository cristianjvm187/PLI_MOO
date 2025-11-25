import numpy as np
from solver.Tools import *
import time
from solver.Convex_hull import *

eps = 1e-5


class PLIe:
    def __init__(self, m, objetivos, F, puentes, W, H, delta):
        """
        m - cantidad de objetivos
        objetivos - np.array de mx2 con los puntos objetivos
        F - un array de len m donde F[i]=1 indica que quiero estar cerca
        del punto objetivos[i] y si F[i]=-1 quiero estar lejos objetivos[i]
        puentes - array con la posicion de los puentes en el plano
        p1s,p1n,p2s,p2n
        """
        self.m = m
        self.objetivos = objetivos
        self.F = F
        self.p1s = puentes[0]
        self.p1n = puentes[1]
        self.p2s = puentes[2]
        self.p2n = puentes[3]
        self.delta = delta
        self.RS = puentes[0][1]
        self.RN = puentes[1][1]
        self.x1 = puentes[0][0]
        self.x2 = puentes[2][0]
        self.diam = self.RN - self.RS
        self.W = W
        self.H = H

    def posicion(self, x):
        """
        x es un punto de R2
        Devuelve 1 si se encuetra al norte del rio
        Devuelve -1 si se encuetra al sur
        Devuelve 0 si se encuetra en el rio
        """
        if x[1] - self.RN >= 0:
            return 1
        if self.RS - x[1] >= 0:
            return -1
        return 0

    def dist(self, x, pto, c):
        if self.posicion(x) == self.posicion(pto):
            return c * l2(x, pto)
        else:
            if self.posicion(x) == 1:
                D1 = l2(x, self.p1n) + self.diam + l2(self.p1s, pto)
                D2 = l2(x, self.p2n) + self.diam + l2(self.p2s, pto)
                return c * min(D2, D1)
            elif self.posicion(x) == -1:
                D1 = l2(x, self.p1s) + self.diam + l2(self.p1n, pto)
                D2 = l2(x, self.p2s) + self.diam + l2(self.p2n, pto)
                return c * min(D2, D1)

    def evaluar(self, x):
        """
        x es el punto de R2 que quiero saber su evaluacion en la funcion F del modelo
        devuelve un vector con la distancia relativa a cada objetivo
        si F[i]=-1 la distancia es negativa
        """
        eval = []
        for i in range(self.m):
            eval.append(self.dist(x, self.objetivos[i], self.F[i]))

        return np.array(eval)

    def clarke_subdiferencial(self, x: np.ndarray, point: np.ndarray):
        """
        Calcular el subdiferencial en el punto x
        """
        if self.posicion(x) == self.posicion(point):
            norm = np.linalg.norm(x - point)
            # print("calrke", x, point, [(x - point) / norm])
            return [2 * (x - point)]
        else:
            if self.posicion(x) == 1:
                if (
                    abs(
                        l2(x, self.p1n)
                        + l2(point, self.p1s)
                        - (l2(x, self.p2n) + l2(point, self.p2s))
                    )
                    < eps
                ):
                    return [
                        2 * (x - self.p1n),
                        2 * (x - self.p2n),
                    ]
                else:
                    if l2(x, self.p1n) + l2(point, self.p1s) < l2(x, self.p2n) + l2(
                        point, self.p2s
                    ):
                        return [2 * (x - self.p1n)]
                    else:
                        return [2 * (x - self.p2n)]
            else:
                if (
                    abs(
                        l2(x, self.p1s)
                        + l2(point, self.p1n)
                        - (l2(x, self.p2s) + l2(point, self.p2n))
                    )
                    < eps
                ):
                    return [
                        2 * (x - self.p1s),
                        2 * (x - self.p2s),
                    ]
                else:
                    if l2(x, self.p1s) + l2(point, self.p1n) < (
                        l2(x, self.p2s) + l2(point, self.p2n)
                    ):
                        return [2 * (x - self.p1s)]
                    else:
                        return [2 * (x - self.p2s)]

    def direccion_descenso(self, x):
        obj = self.objetivos
        sub_gradientes = []
        for i in range(self.m):
            if (np.linalg.norm(x - obj[i])) < eps:
                return np.array([0, 0])
            else:
                aux = [
                    self.F[i] * temp for temp in self.clarke_subdiferencial(x, obj[i])
                ]
                sub_gradientes.extend(aux)
        aux = []
        for elem in sub_gradientes:
            check = True
            for a in aux:
                if np.linalg.norm(a - elem) < eps:
                    check = False
            if check:
                aux.append(elem)
        sub_gradientes = np.array(aux)
        if len(sub_gradientes) > 1:
            hull = convex_hull_Graham(sub_gradientes)
            y = punto_distancia_minima_al_origen(hull)
            d = y[0]
            return d
        else:
            return sub_gradientes[0]

    def dominacia(self, x, y, C):
        """
        Devuelve True si x domina a y
        Devuelve False si x no domina a y
        """
        check = True
        for i in range(self.m):
            eval_y = self.dist(y, self.objetivos[i], self.F[i])
            eval_x = self.dist(x, self.objetivos[i], self.F[i])
            if eval_y + C < eval_x:
                return False
        return True

    def armijo(self, x, t0, d, c_armijo, alpha):
        """
        t0 - tamaño de paso inicial
        d - direccion de descenso
        c_armijo - coeficente armijo
        alpha - regulador
        """
        t = t0
        while True:
            y = x + t * d

            if self.dominacia(y, x, -t * alpha * np.linalg.norm(d)):
                return t
            else:
                if t < eps:
                    return t
                t = t * c_armijo

    def Nonsmooth_descent_method(self, x0, t0, c_armijo, alpha, L):
        """
        ribera - indica sobre cual ribera estamos construyendo la solucion
        x0 - es el punto inicial
        t0 - es el tamaño de paso
        c_armijo - coeficiente de armijo
        alpha- regularizador
        L- Limite de iteraciones
        Devueve x como solucion final,
        path el camino de puntos por el que paso,
        """
        x = x0
        path = [x]
        t = t0
        if self.posicion(x) == 1:
            ribera = 1
        else:
            ribera = -1
        for _ in range(L):
            v = self.direccion_descenso(x)
            if np.linalg.norm(v) < eps:
                return x, path, "pto_estacionario"
            if ribera == 1:
                if len(lado_borde(x, 0, self.W, self.RN + self.delta, self.H, eps)) > 0:
                    v = proyectar_direccion(
                        x, -v, 0, self.W, self.RN + self.delta, self.H, eps
                    )
                else:
                    v = -v
                if np.linalg.norm(v) < eps:
                    return x, path, "pto_estacionario"
                t0 = len_skip(x, v, 0, self.W, self.RN + self.delta, self.H)
                # print("paso", t0)
            else:
                # print(x, v)
                if len(lado_borde(x, 0, self.W, 0, self.RS - self.delta, eps)) > 0:
                    # print("mate")
                    v = proyectar_direccion(
                        x, -v, 0, self.W, 0, self.RS - self.delta, eps
                    )
                else:
                    v = -v
                # print("con que entro ", v)
                if np.linalg.norm(v) < eps:
                    return x, path, "pto_estacionario"
                t0 = len_skip(x, v, 0, self.W, 0, self.RS - self.delta)
            t = self.armijo(x, t0, v, c_armijo, alpha)
            # print("tamaño de apso", t0, t)
            if abs(t) < eps:
                return x, path, "len_paso"
            # print(t * v)
            x = x + t * v
            if ribera == 1:
                x = projection(x, 0, self.W, self.RN + self.delta, self.H)
            else:
                x = projection(x, 0, self.W, 0, self.RS - self.delta)
            path.append(x)
        return x, path, "num_iteraciones"
