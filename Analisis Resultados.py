import json
from collections import defaultdict


def analyze_results(json_data):
    # 1. Obtener el tiempo de ejecución
    execution_time = json_data["results"]["tiempo"]

    # Función auxiliar para contar soluciones válidas y únicas
    def count_valid_solutions(solutions):
        valid_solutions = [sol for sol in solutions if sol != [-1.0, -1.0]]
        unique_solutions = defaultdict(int)

        for sol in valid_solutions:
            # Redondear a 5 decimales para considerar soluciones "iguales"
            rounded = (round(sol[0], 6), round(sol[1], 6))
            unique_solutions[rounded] += 1

        return {
            "total_valid": len(valid_solutions),
            "unique_count": len(unique_solutions),
            "unique_solutions": dict(unique_solutions),
        }

    # 2. Analizar fase 0
    fase0_results = count_valid_solutions(json_data["results"]["fase0"])

    # 3. Analizar fase 1
    fase1_results = count_valid_solutions(json_data["results"]["fase1"])

    # 4. Analizar fase 2
    fase2_results = count_valid_solutions(json_data["results"]["fase2"])

    return {
        "execution_time": execution_time,
        "fase0": fase0_results,
        "fase1": fase1_results,
        "fase2": fase2_results,
    }


def print_results(analysis):
    print(f"Tiempo de ejecución del algoritmo: {analysis['execution_time']} segundos")

    print("\nFase 0 (Inicial):")
    print(f"- Soluciones válidas (no [-1,-1]): {analysis['fase0']['total_valid']}")
    print(f"- Soluciones únicas: {analysis['fase0']['unique_count']}")

    print("\nFase 1:")
    print(f"- Soluciones válidas (no [-1,-1]): {analysis['fase1']['total_valid']}")
    print(f"- Soluciones únicas: {analysis['fase1']['unique_count']}")

    print("\nFase 2:")
    print(f"- Soluciones válidas (no [-1,-1]): {analysis['fase2']['total_valid']}")
    print(f"- Soluciones únicas: {analysis['fase2']['unique_count']}")


# Ejemplo de uso
if __name__ == "__main__":
    # Cargar el JSON (en este caso sería desde un archivo)
    with open("Resultados/Experimento 10_m_resultados.json") as f:
        data = json.load(f)

    analysis = analyze_results(data)
    print_results(analysis)
# Ejemplo de uso
