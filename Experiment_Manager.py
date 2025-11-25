import json
from solver.Solver import run_solver_with_config, save_results_to_json


def main(name):
    # Cargar parámetros
    with open("Experimentos/" + name + ".json", "r") as f:
        params = json.load(f)

    # Ejecutar para ambos modelos
    for model in ["m", "e"]:
        resultados = run_solver_with_config(params, model)
        model = name + "_" + model
        save_results_to_json(resultados, model, params)


if __name__ == "__main__":
    name = "Experimento"
    main(name + str(25))
