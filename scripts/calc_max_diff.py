"""
Script zum Ausrechnen der gößten von uns gefressenden Biester nach ID
"""


def extract_energy(line):
    """
    Gibt für eine Zeile der Log-Datei die ID und den Energiewert zurück, falls
    die Zeile diese Informationen enthält, ansonsten wird None für beide Werte
    zurückgegeben

    Args:
        line: ausgelesene Zeil einer Log-Datei

    Returns:
        id: id von dem Biest, welches diesen Schritt ausführt
        energy: Energiewert des Biest
    """

    parts = line.split()
    if len(parts) < 3 or parts[0] != "id_energy_env":
        return None, None
    id_part = parts[2].removeprefix("'").split("#")[0]
    energy_str = parts[2].split("#")[1]
    try:
        energy = float(energy_str)
    except ValueError:
        return None, None
    return id_part, energy


def calculate_max_differences_by_id(energy_list):
    """
    Rechnet für jede ID die maximal Differenz an Punkten zwischen zwei
    aufeinander folgenden Schritten aus.

    Args:
        energy_list: List aus Tupeln (id, energy) für jeden Schritt eines Biests

    Returns:
        max_diff_by_id: Dictionary mit den IDs als keys und die maximale Differenz als value
    """
    # Sortiere die Liste nach der id
    sorted_list = sorted(energy_list, key=lambda x: x[0])

    max_diff_by_id = {}
    last_energy_by_id = {}

    for biest_id, energy in sorted_list:
        if biest_id not in max_diff_by_id:
            max_diff_by_id[biest_id] = 0
        else:
            max_diff_by_id[biest_id] = max(
                energy - last_energy_by_id[biest_id], max_diff_by_id[biest_id]
            )

        last_energy_by_id[biest_id] = energy
    return max_diff_by_id


def get_id_energy(lines):
    """
    Gibt für die Zeilen einer Log-Datei eine Liste an Tupeln (id, energy) für
    jeden geloggten Schritt zurück.

    Args:
        lines: alle ausgelesenen Zeilen einer Log-Datei

    Returns:
        id_energy_pairs: Liste von Tupeln (id, energy) für jeden geloggten Schritt
    """

    id_energy_pairs = []

    for line in lines:
        biest_id, energy = extract_energy(line)
        if biest_id is not None and energy is not None:
            id_energy_pairs.append((biest_id, energy))

    return id_energy_pairs


# Befehl zum herunterladen der Log-Dateien:
# scp gruppe03@arena.informatik.hs-augsburg.de:/home/gruppe03/logs/* ~/Downloads/logs/
# Liest Zeilen aus Log-Datei aus
with open(
    "/home/pyoneer/Downloads/logs/simulation_2025-11-12_06-01-01.log", "r"
) as file:
    file_lines = file.readlines()

print(calculate_max_differences_by_id(get_id_energy(file_lines)))
