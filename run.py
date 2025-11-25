import json
from solver.Solver import run_solver_with_config
from datetime import datetime
import numpy as np


def convert_numpy_types(obj):
    """
    Convierte tipos de datos NumPy a tipos nativos de Python
    """
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj


def save_results_to_json(results, model_name, params):
    """Guarda los resultados en un archivo JSON con marca de tiempo y parámetros."""

    # Preparar el diccionario de resultados
    temp_result = []
    for i in range(len(results) - 2):
        temp_result.append(convert_numpy_types(results[i]))
    temp_result.append(results[8])
    temp_result.append(results[9])
    results = temp_result

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
