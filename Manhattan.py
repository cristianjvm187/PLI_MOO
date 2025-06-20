import numpy as np
from Tools import *
import time

eps = 1e-5


class PLIm:
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

    def evaluar(self, x):
        """
        x es el punto de R2 que quiero saber su evaluacion en la funcion F del modelo
        devuelve un vector con la distancia relativa a cada objetivo
        si F[i]=-1 la distancia es negativa
        """
        eval = []
        for i in range(self.m):
            if self.posicion(x) == self.posicion(self.objetivos[i]):
                eval.append(self.F[i] * l1(x, self.objetivos[i]))
            else:
                if self.posicion(x) == 1:
                    D1 = l1(x, self.p1n) + self.diam + l1(self.p1s, self.objetivos[i])
                    D2 = l1(x, self.p2n) + self.diam + l1(self.p2s, self.objetivos[i])
                    eval.append(self.F[i] * min(D2, D1))
                elif self.posicion(x) == -1:
                    D1 = l1(x, self.p1s) + self.diam + l1(self.p1n, self.objetivos[i])
                    D2 = l1(x, self.p2s) + self.diam + l1(self.p2n, self.objetivos[i])
                    eval.append(self.F[i] * min(D2, D1))
        return np.array(eval)

    def clarke_subdiferencial(self, x, objetivo):
        """
        Calcula el subdiferencial de clarke en x teniedo en cuenta
        el punto dado por objetivo
        Devuelve un array con los limites del subdiferencial
        """
        a = objetivo[0]
        b = objetivo[1]

        if self.posicion(x) == self.posicion(objetivo) and abs(self.posicion(x)) == 1:
            # print("esto ", x, objetivo)
            if abs(x[0] - a) < eps and abs(x[1] - b) < eps:
                return np.array([[-1, -1], [-1, 1], [1, -1], [1, 1]])
            elif abs(x[0] - a) < eps:
                return np.array([[-1, sgn(x[1] - b)], [1, sgn(x[1] - b)]])
            elif abs(x[1] - b) < eps:

                return np.array([[sgn(x[0] - a), -1], [sgn(x[0] - a), 1]])
            else:
                # print("x entro aqui")
                return np.array([[sgn(x[0] - a), sgn(x[1] - b)]])

        else:
            if self.posicion(x) == 1:
                # print("Estoy en el norte")
                C1 = l1(self.p1s, objetivo)
                C2 = l1(self.p2s, objetivo)
                if (C2 - C1) - (self.x2 - self.x1) >= 0:
                    # print(x, "por el puente 1 es mas corto")
                    return self.clarke_subdiferencial(x, self.p1n)
                elif (C1 - C2) - (self.x2 - self.x1) >= 0:
                    # print(x, "por el puente 2 es mas corto")
                    return self.clarke_subdiferencial(x, self.p2n)
                else:
                    lim = (self.x2 + self.x1 + C2 - C1) / 2
                    if abs(x[0] - lim) < eps:
                        return np.array([[-1, 1], [1, -1]])
                    elif x[0] - lim > eps:
                        return self.clarke_subdiferencial(x, self.p2n)
                    else:
                        return self.clarke_subdiferencial(x, self.p1n)
            elif self.posicion(x) == -1:
                # print("estoy en el sur")
                C1 = l1(self.p1n, objetivo)
                C2 = l1(self.p2n, objetivo)
                if (C2 - C1) - (self.x2 - self.x1) >= 0:
                    return self.clarke_subdiferencial(x, self.p1s)
                elif (C1 - C2) - (self.x2 - self.x1) >= 0:
                    return self.clarke_subdiferencial(x, self.p2s)
                else:
                    lim = (self.x2 + self.x1 + C2 - C1) / 2
                    if abs(x[0] - lim) < eps:
                        return np.array([[-1, -1], [1, -1]])
                    elif x[0] - lim > eps:
                        return self.clarke_subdiferencial(x, self.p2s)
                    else:
                        return self.clarke_subdiferencial(x, self.p1s)

    def direccion_descenso(self, x):

        sub_gradientes = []
        for i in range(self.m):
            temp = self.clarke_subdiferencial(x, self.objetivos[i])
            for grad in temp:
                sub_gradientes.append(self.F[i] * grad)

        aux = []

        for elem in sub_gradientes:
            check = True
            for a in aux:
                if np.linalg.norm(a - elem) < eps:
                    check = False
            if check:
                aux.append(elem)
        sub_gradientes = np.array(aux)
        # debug
        # print("pto", x)
        # print("subgradientes", sub_gradientes)

        if len(sub_gradientes) >= 3:
            return np.array([0, 0])
        elif len(sub_gradientes) == 1:
            return sub_gradientes[0]
        else:
            if colinear(sub_gradientes[0], sub_gradientes[1]):
                return np.array([0, 0])
            else:
                return (sub_gradientes[0] + sub_gradientes[1]) / 2

    def dominacia(self, x, y, C):
        """
        Devuelve True si x domina a y
        Devuelve False si x no domina a y
        """
        check = True
        eval_x = self.evaluar(x)
        eval_y = self.evaluar(y)
        # quizas falta el caso donde la evaluacion es igual
        # print(x, y)
        # print("x", eval_x)
        # print("y", eval_y)
        # print(C)
        for i in range(self.m):
            if self.F[i] == 1:
                if eval_y[i] + C < eval_x[i]:
                    # print("distr", x, y)
                    return False
            else:
                if abs(eval_y[i]) - C > abs(eval_x[i]):
                    return False
        # print(x, "domina a ", y)
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
            # print("YQYQWdqw", x, v)
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
