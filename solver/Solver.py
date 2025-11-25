from solver.Euclidian import *
from solver.Manhattan import *
import random
import time
import json
from datetime import datetime


def solver(modelo, m, W, H, points, F, bridges, delta, n_sol, t, armijo, alpha, lim):

    if modelo == "e":
        Example = PLIe(m, points, F, bridges, W, H, delta)
    else:
        Example = PLIm(m, points, F, bridges, W, H, delta)
    near = []
    far = []
    for i in range(m):
        if F[i] > 0:
            near.append(points[i])
        else:
            far.append(points[i])
    near = np.array(near)
    far = np.array(far)

    sol_N0 = []
    inicial_N = []
    detencion_N = []
    sol_S0 = []
    inicial_S = []
    detencion_S = []
    inicial = []

    sol_N1 = []
    info_fas1N = {}
    sol_S1 = []
    info_fas1S = {}
    sol_N2 = []
    info_fas2N = {}
    sol_S2 = []
    info_fas2S = {}
    detencion = []

    temp = time.time()
    for _ in range(n_sol):
        x = Example.Nonsmooth_descent_method(
            inicial_point(0, Example.W, Example.RN + Example.delta, Example.H),
            t,
            armijo,
            alpha,
            lim,
        )
        sol_N0.append(x[1][-1])
        inicial_N.append(x[1][0])
        detencion_N.append(x[2])

    for _ in range(n_sol):
        x = Example.Nonsmooth_descent_method(
            inicial_point(0, Example.W, 0, Example.RS - Example.delta),
            t,
            armijo,
            alpha,
            lim,
        )
        sol_S0.append(x[1][-1])
        inicial_S.append(x[1][0])
        detencion_S.append(x[2])

    for i in range(len(sol_N0)):
        check = True
        for j in range(len(sol_S0)):
            if Example.dominacia(sol_S0[j], sol_N0[i], 0):
                check = False
                break
        for j in range(len(sol_N0)):
            if i != j:
                if Example.dominacia(sol_N0[j], sol_N0[i], 0):
                    check = False
                    break
        if check:
            info_fas2N[str(i)] = sol_N0[i]
            sol_N2.append(sol_N0[i])

    for i in range(len(sol_S0)):
        check = True
        for j in range(len(sol_N0)):
            if Example.dominacia(sol_N0[j], sol_S0[i], 0):
                check = False
        for j in range(len(sol_S0)):
            if i != j:
                if Example.dominacia(sol_S0[j], sol_S0[i], 0):
                    check = False
                    break
        if check:
            info_fas2S[str(i + n_sol)] = sol_S0[i]
            sol_S2.append(sol_S0[i])

    tiempo = time.time() - temp

    for i in range(len(sol_N0)):
        check = True
        for j in range(len(sol_S0)):
            if Example.dominacia(sol_S0[j], sol_N0[i], 0):
                check = False
                break
        if check:
            info_fas1N[str(i)] = sol_N0[i]
            sol_N1.append(sol_N0[i])

    for i in range(len(sol_S0)):
        check = True
        for j in range(len(sol_N0)):
            if Example.dominacia(sol_N0[j], sol_S0[i], 0):
                check = False
        if check:
            info_fas1S[str(i)] = sol_S0[i]
            sol_S1.append(sol_S0[i])

    fase1 = []
    fase1.extend(sol_N1)
    fase1.extend(sol_S1)
    fase1 = np.array(fase1)

    fase2 = []
    fase2.extend(sol_N2)
    fase2.extend(sol_S2)
    fase2 = np.array(fase2)

    fase0 = []
    fase0.extend(sol_N0)
    fase0.extend(sol_S0)
    fase0 = np.array(fase0)

    state_fase2 = []
    # print(info_fas1N.keys())
    for i in range(2 * n_sol):
        if i < n_sol:
            if str(i) in info_fas2N.keys():
                state_fase2.append(tuple(info_fas2N[str(i)]))
            else:
                state_fase2.append(tuple([-1, -1]))
        else:
            if str(i) in info_fas2S.keys():
                state_fase2.append(tuple(info_fas2S[str(i)]))
            else:
                state_fase2.append(tuple([-1, -1]))

    state_fase1 = []
    for i in range(2 * n_sol):
        if i < n_sol:
            if str(i) in info_fas1N.keys():
                state_fase1.append(tuple(info_fas1N[str(i)]))
            else:
                state_fase1.append(tuple([-1, -1]))
        else:
            if str(i) in info_fas1S.keys():
                state_fase1.append(tuple(info_fas1S[str(i)]))
            else:
                state_fase1.append(tuple([-1, -1]))

    state_fase2 = np.array(state_fase2)
    state_fase1 = np.array(state_fase1)
    detencion.extend(detencion_N)
    detencion.extend(detencion_S)
    inicial.extend(inicial_N)
    inicial.extend(inicial_S)
    inicial = np.array(inicial)

    return (
        near,
        far,
        inicial,
        fase0,
        fase1,
        fase2,
        state_fase1,
        state_fase2,
        detencion,
        tiempo,
    )


def run_solver_with_config(params, model):
    """Ejecuta el solver con parámetros y modelo específico"""

    random.seed(params["seed"])
    np.random.seed(params["seed"])

    return solver(
        modelo=model,
        m=params["m"],
        W=params["W"],
        H=params["H"],
        points=np.array(params["points"]),
        F=np.array(params["F"]),
        bridges=np.array(params["bridges"]),
        delta=params["delta"],
        n_sol=params["n_sol"],
        t=params["t"],
        armijo=params["armijo"],
        alpha=params["alpha"],
        lim=params["lim"],
    )
