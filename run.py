import json
from solver.Solver import run_solver_with_config
from datetime import datetime


def save_results_to_json(results, model_name, params):
    """Guarda los resultados en un archivo JSON con marca de tiempo y parámetros."""

    # Preparar el diccionario de resultados
    temp_result = []
    for i in range(len(results) - 2):
        aux = []
        for x in results[i]:
            aux.append(list(x))
        temp_result.append(aux)

    temp_result.append(results[8])
    temp_result.append(results[9])
    results = temp_result
    print(results)
    results_dict = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "parameters": params,
        "results": {
            "near": results[0],
            "far": results[1],
            "inicial": results[2],
            "fase0": results[3],
            "fase1": results[4],
            "fase2": results[5],
            "state_fase1": results[6],
            "state_fase2": results[7],
            "detencion": results[8],
            "tiempo": results[9],
        },
    }
    # Nombre del archivo basado en el modelo y timestamp
    filename = f"{model_name}_resultados.json"
    with open("Resultados/" + filename, "w") as f:
        print(model_name)
        json.dump(results_dict, f, indent=4)
    print(f"Resultados guardados en {filename}")


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
    name = "Experimento "
    num = input("Introducir # de experimento: ")
    main(name + num)
