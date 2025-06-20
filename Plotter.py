import matplotlib.pyplot as plt
import numpy as np
import json


def plotter(
    W, H, near_points, far_points, bridges, sol_points, model_name, num, ide, c="black"
):
    plt.figure(figsize=(8, 8))

    # --- Tamaños personalizados ---
    sizes = {
        "near": 40,
        "far": 40,
        "bridges": 70,
        "solutions": 18,
        "inicial": 20,
        "e": 30,
        "m": 15,
        "i": 25,
    }

    # --- Río ---
    n = bridges[-1][1] if bridges.size else 0
    s = bridges[0][1] if bridges.size else 0
    plt.hlines(
        n, 0, W, colors="royalblue", linewidth=2.5, linestyles="dashed", zorder=1
    )
    plt.hlines(
        s, 0, W, colors="royalblue", linewidth=2.5, linestyles="dashed", zorder=1
    )

    # --- Puentes ---
    if bridges.size:
        plt.scatter(
            bridges[:, 0],
            bridges[:, 1],
            color="blue",
            s=sizes["bridges"],
            marker="d",
            zorder=2,
            label="Puentes",
        )

    # --- Soluciones ---
    if model_name in ["e", "m", "i"]:
        if len(sol_points):
            markers = {"e": ".", "m": "s", "i": "x"}
            labels = {
                "e": f"Sol Euclidiana",
                "m": f"Sol Manhattan",
                "i": "Puntos Iniciales",
            }
            plt.scatter(
                sol_points[:, 0],
                sol_points[:, 1],
                color=c,
                marker=markers[model_name],
                s=sizes[model_name],
                edgecolors="k",
                linewidths=0.3,
                zorder=3,
                label=labels[model_name],
            )

    # --- Near Points ---
    if near_points.size:
        plt.scatter(
            near_points[:, 0],
            near_points[:, 1],
            color="green",
            s=sizes["near"],
            zorder=4,
            label="Near",
        )

    # --- Far Points ---
    if far_points.size:
        plt.scatter(
            far_points[:, 0],
            far_points[:, 1],
            color="red",
            s=sizes["far"],
            zorder=5,
            label="Far",
        )

    # --- Ajustes finales ---
    plt.xlim(-1, W + 1)
    plt.ylim(-1, H + 1)
    plt.grid(True, zorder=0, linestyle="--", alpha=0.7)
    plt.gca().set_aspect("equal")
    plt.legend(loc="upper right", fontsize=8)

    # --- Sistema de guardado mejorado ---
    name_map = {
        "0": f"Exp{num} Configuracion",
        "1": f"Exp{num} Inicial",
        "2": f"Exp{num} Fase0 Manhattan",
        "3": f"Exp{num} Fase1 Manhattan",
        "4": f"Exp{num} Fase2 Manhattan",
        "5": f"Exp{num} Fase0 Euclidiana",
        "6": f"Exp{num} Fase1 Euclidiana",
        "7": f"Exp{num} Fase2 Euclidiana",
    }

    filename = name_map.get(ide, f"Exp{num} Desconocido")
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()  # Cierra la figura para liberar memoria


def Extraer(num):
    info = []

    with open(f"Resultados/Experimento {str(num)}_m_resultados.json", "r") as ar:
        data = json.load(ar)

        # Extraer parámetros básicos
        W = data["parameters"]["W"]
        H = data["parameters"]["H"]
        info.append(W)
        info.append(H)

        # Convertir arrays a numpy
        near_points = np.array(data["results"]["near"])
        far_points = np.array(data["results"]["far"])
        bridges = np.array(data["parameters"]["bridges"])

        # Seleccionar puntos solución (usamos fase2 como ejemplo)
        sol_fase0 = np.array(data["results"]["fase0"])
        sol_fase1 = np.array(data["results"]["fase1"])
        sol_fase2 = np.array(data["results"]["fase2"])
        inicial = np.array(data["results"]["inicial"])
        info.append(near_points)
        info.append(far_points)
        info.append(bridges)
        info.append(inicial)
        info.append(sol_fase0)
        info.append(sol_fase1)
        info.append(sol_fase2)

    with open(f"Resultados/Experimento {str(num)}_e_resultados.json", "r") as ar:
        data = json.load(ar)
        sol_fase0 = np.array(data["results"]["fase0"])
        sol_fase1 = np.array(data["results"]["fase1"])
        sol_fase2 = np.array(data["results"]["fase2"])

        info.append(sol_fase0)
        info.append(sol_fase1)
        info.append(sol_fase2)

    return info


if __name__ == "__main__":
    """
    Info =[W,H,[near],[far],[bridges],[inicial],[fase0m],[fase1m],[fase2m],[fase0e],[fase1e],[fase2e]]
    """
    for num in range(10, 11):
        info = Extraer(num)
        plotter(
            info[0], info[1], info[2], info[3], info[4], np.array([]), "p", num, "0"
        )
        plotter(info[0], info[1], info[2], info[3], info[4], info[5], "i", num, "1")
        plotter(info[0], info[1], info[2], info[3], info[4], info[6], "m", num, "2")
        plotter(info[0], info[1], info[2], info[3], info[4], info[7], "m", num, "3")
        plotter(info[0], info[1], info[2], info[3], info[4], info[8], "m", num, "4")
        plotter(info[0], info[1], info[2], info[3], info[4], info[9], "e", num, "5")
        plotter(info[0], info[1], info[2], info[3], info[4], info[10], "e", num, "6")
        plotter(info[0], info[1], info[2], info[3], info[4], info[11], "e", num, "7")
