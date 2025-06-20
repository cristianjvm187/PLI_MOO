from Manhattan import *
import random


def FB(N, m, points, puentes, W, H, F, delta):
    Example = PLI(m, points, F, puentes, W, H, delta)
    sol_N = []
    sol_S = []
    ini = []
    for i in range(N):
        x = np.array(
            [
                random.uniform(0, Example.W),
                random.uniform(Example.RN + delta, Example.H),
            ]
        )
        ini.append(x)
        sol_N.append(x)

    for i in range(N):
        x = np.array(
            [random.uniform(0, Example.W), random.uniform(0, Example.RS - delta)]
        )
        ini.append(x)
        sol_S.append(x)

    sol = []
    for i in range(N):
        check = True
        for j in range(N):
            if Example.dominacia(sol_S[j], sol_N[i], 0):
                check = False
                break
        for j in range(N):
            if i != j and Example.dominacia(sol_N[j], sol_N[i], 0):
                check = False
                break
        if check:
            sol.append(sol_N[i])
    for i in range(N):
        check = True
        for j in range(N):
            if Example.dominacia(sol_N[j], sol_S[i], 0):
                check = False
                break
        for j in range(N):
            if i != j and Example.dominacia(sol_S[j], sol_S[i], 0):
                check = False
                break
        if check:
            sol.append(sol_S[i])

    near = []
    far = []
    for i in range(m):
        if F[i] > 0:
            near.append(points[i])
        else:
            far.append(points[i])
    near = np.array(near)
    far = np.array(far)
    sol = np.array(sol)
    ini = np.array(ini)
    plotter(W, H, near, far, puentes, ini)
    plotter(W, H, near, far, puentes, sol)
