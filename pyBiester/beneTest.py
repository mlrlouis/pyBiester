from bene_strategie import BeastBrain


def print_env(env_str):
    size = int(len(env_str) ** 0.5)
    for i in range(size):
        print(" ".join(env_str[i * size : (i + 1) * size]))
    print()


def run_scenario(name, env, n=3, beast_id=1, energy=150, brain=None):
    if brain is None:
        brain = BeastBrain(n)
    print(f"--- Szenario: {name} ---")
    print_env(env)

    server_command = brain.decide(beast_id, energy, env)
    print(f"Server-String: {server_command}")

    parts = server_command.split()
    action = parts[1]
    if action in ["MOVE", "SPLIT"]:
        dx, dy = int(parts[2]), int(parts[3])
        print(f"Entscheidung: {action}, Bewegung: ({dx},{dy})\n")
    else:
        print(f"Entscheidung: {action}\n")


if __name__ == "__main__":
    empty = ["." for _ in range(25)]
    center = 12  # Mitte 5x5

    scenarios = []

    # --- Basis-Szenarien ---
    env = empty.copy()
    env[center] = "B"
    env[7] = "*"  # Food oben
    scenarios.append(("Food 1 Feld oben", "".join(env)))

    env = empty.copy()
    env[center] = "B"
    env[17] = "<"  # Schwächer unten
    scenarios.append(("Weaker 1 Feld unten", "".join(env)))

    # --- Test: Reproduktion möglich ---
    env = empty.copy()
    env[center] = "B"
    scenarios.append(
        ("Reproduktion möglich, freie Nachbarfelder", "".join(env))
    )

    # --- Test: Reproduktion blockiert durch stärkeren Gegner ---
    env = empty.copy()
    env[center] = "B"
    env[11] = ">"  # links stärker
    scenarios.append(
        ("Reproduktion blockiert durch stärkeren Gegner", "".join(env))
    )

    # --- Test: Verwandte vermeiden ---
    env = empty.copy()
    env[center] = "B"
    env[7] = "#"  # oben Verwandter
    env[17] = "<"  # unten Schwächer
    scenarios.append(("Verwandte vermeiden", "".join(env)))

    # --- Test: Split-Limit prüfen ---
    env = empty.copy()
    env[center] = "B"
    env[7] = "<"
    # Biest hat 2 Splits schon gemacht
    brain = BeastBrain(n=3)
    brain.split_count[1] = 2
    scenarios.append(("Split-Limit überschritten", "".join(env)))

    for name, env in scenarios:
        energy = 60_000 if "Reproduktion" in name else 250
        # Beim Split-Limit-Szenario das bereits initialisierte Brain benutzen
        if name == "Split-Limit überschritten":
            run_scenario(
                name, env, n=3, beast_id=1, energy=energy, brain=brain
            )
        else:
            run_scenario(name, env, n=3, beast_id=1, energy=energy)

    # --- Zusätzlicher Testfall aus Logdatei ---
    print("\n" + "=" * 60)
    print("Zusätzlicher Test: Illegaler Move (3, 0) aus Logdatei\n")

    # Logzeile aus dem Fehler:
    # id_energy_env = '12#41.113650482627335#...........................*.....................'
    env_str = "...........................*....................."

    brain = BeastBrain(n=3)
    run_scenario(
        "Illegaler Move aus Logdatei",
        env_str,
        n=3,
        beast_id=12,
        energy=41.113650482627335,
        brain=brain,
    )

    # Optional: automatische Prüfung, ob Schrittgröße erlaubt ist
    cmd = brain.decide(12, 41.113650482627335, env_str)
    parts = cmd.split()
    if parts[1] in ["MOVE", "SPLIT"]:
        dx, dy = int(parts[2]), int(parts[3])
        if abs(dx) > 2 or abs(dy) > 2:
            print(f"❌ FEHLER: Illegaler Move erkannt ({dx}, {dy})!")
        else:
            print(f"✅ Move legal ({dx}, {dy})")
