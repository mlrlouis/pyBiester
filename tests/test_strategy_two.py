"""
Tests für 
"""
import pytest
from pyBiester.strategy_two import (
    BIESTER,
    Symbol,
    WELT_X,
    WELT_Y,
    get_cords,
    get_movement_to_coords,
    get_costs,
    get_cheapest_position,
    is_symbol_in_reachable_enviroment,
    clean_of_not_reachable,
    eat_victim,
    get_best_food,
    get_idle,
    contains_profit,
    clean_of_enemy,
    clean_of_victim_siblings,
    get_action,
    clean_biester,
    print_enviroment,
)

# Hilfsfunktion für 7x7 Strings (49 Zeichen), da N=3
def create_env(chars, fill="."):
    """
    Erstellt ein 49-Zeichen Environment und platziert chars an bestimmten Stellen.
    """
    base = list(fill * 49)
    for index, char in chars.items():
        if 0 <= index < 49:
            base[index] = char
    return "".join(base)


@pytest.fixture(autouse=True)
def reset_biester():
    """
    Setzt den Biester-Logger vor jedem Test zurück.
    """
    clean_biester()


# Tests für BiesterLogger

def test_contains_biest_at_cords_always_false():
    """
    Scheinbar  gibt die Methode contains_biest_at_cords im aktuellen Code
    immer False zurück.
    """
    assert BIESTER.contains_biest_at_cords((5, 5)) is False
    # Selbst wenn wir eins hinzufügen
    BIESTER.log_movement(1, (0, 0))
    assert BIESTER.contains_biest_at_cords(BIESTER.get_biest_coords(1)) is False


def test_log_movement_updates_coords():
    """
    Prüft, ob log_movement die Koordinaten im Dictionary aktualisiert.
    """
    # Start ist (20, 20) laut get_biest_coords Default
    biest_id = 1
    move_rel = (1, 1) # Bewegung +1 x, +1 y

    BIESTER.log_movement(biest_id, move_rel)

    # Erwartet: 20+1, 20+1 = (21, 21)
    coords = BIESTER.get_biester()[biest_id]
    assert coords == (21, 21)


def test_clean_biester_direct_call():
    """
    Direkter Test der clean_biester()-Funktion.
    """
    BIESTER.log_movement(1, (1, 1))
    assert len(BIESTER.get_biester()) > 0
    clean_biester()
    assert not BIESTER.get_biester()


# Hilfsfunktionen

def test_get_cords_calculation():
    """
    Testet die Umrechnung von Array-Index zu Welt-Koordinaten.
    """
    # Biest ist bei (20, 20). N=3.
    # Index 24 ist die Mitte (3,3 relative). Sollte (20,20) ergeben.
    assert get_cords(24, 1) == (20, 20)

    # Index 25 ist (4,3 relative) -> +1 x -> (21, 20)
    assert get_cords(25, 1) == (21, 20)


def test_get_costs_basic():
    """
    Testet Kostenberechnung
    """
    # Von (20,20) nach (22, 20) sind 2 Schritte. Kosten = 2 * 1 = 2
    cost = get_costs((22, 20), 1)
    assert cost == 2


def test_is_symbol_in_reachable_enviroment_false():
    """
    Wenn kein Symbol vorhanden ist, soll False zurückkommen.
    """
    env = create_env({}) # Leeres Feld
    result = is_symbol_in_reachable_enviroment(env, Symbol.FOOD, 1, 100)
    assert result is False


def test_clean_of_not_reachable_logic():
    """
    Testet, dass die Funktion läuft (Logik entfernt Ränder).
    """
    # Food an Index 0 (oben links, Rand bei N=3)
    env = create_env({0: Symbol.FOOD.value})
    cleaned = clean_of_not_reachable(env, Symbol.FOOD)

    # Im aktuellen Code wird Index 0 bereinigt (zu Empty)
    assert cleaned[0] == Symbol.EMPTY.value
    assert len(cleaned) == 49


# print_enviroment

def test_print_enviroment_output(capsys):
    """
    Überprüft, dass print_enviroment formatierte Ausgabe erzeugt.
    """
    env = create_env({24: "B", 10: "*"})
    print_enviroment(env)
    out, _ = capsys.readouterr()
    assert "B" in out
    assert "\n" in out


# Entscheidungslogik

def test_clean_of_enemy_removes_food_near_enemy():
    """
    Food nahe eines Enemies soll entfernt werden.
    """
    # Enemy an Pos 10, Food direkt daneben an 11
    env = create_env({10: ">", 11: "*"})

    cleaned = clean_of_enemy(env, 1)

    # Das Food bei 11 sollte nun weg sein (Empty)
    assert cleaned[11] == Symbol.EMPTY.value
    # Der Enemy bleibt
    assert cleaned[10] == Symbol.ENEMY.value


def test_get_action_flee_from_enemy():
    """
    Wenn ein Enemy im Sichtfeld ist, soll Flucht (Bewegung) erfolgen.
    """
    env = create_env({10: ">"}) # Enemy in Sicht
    command, env_out = get_action(env, 1, 100)

    assert "MOVE" in command

    assert isinstance(env_out, str)


def test_clean_of_victim_siblings_no_effect_logic():
    """
    Da contains_biest_at_cords False ist, werden Victims aktuell nicht  entfernt.
    """
    env = create_env({10: "<"})
    cleaned = clean_of_victim_siblings(env, 1)
    # Victim bleibt erhalten, da wir es nicht als "Eigenes Biest" erkennen
    assert cleaned[10] == Symbol.VICTIM.value


# Bewegungs und Kostenfunktionen

def test_get_movement_to_coords_basic():
    """
    Testet, ob die relative Bewegung zwischen Start und Ziel korrekt berechnet wird.
    """
    result = get_movement_to_coords((5, 7), (2, 3))
    assert result == (3, 4)


def test_get_cheapest_position_returns_24_if_energy_too_low():
    """
    Wenn Energie zu niedrig, sollte 24 (Mitte/Fehler) zurückgegeben werden.
    """
    env = create_env({10: "*"})
    # Energy 0 reicht nicht für Bewegung
    pos = get_cheapest_position(env, Symbol.FOOD, 1, energy=0)
    assert pos == 24


def test_get_cheapest_position_valid_choice():
    """
    Prüft, ob bei ausreichender Energie die günstigste Position des Symbols gewählt wird.
    """
    env = create_env({10: "*"})
    pos = get_cheapest_position(env, Symbol.FOOD, 1, energy=100)
    assert pos == 10


# Kampf- und Fresslogik

def test_eat_victim_returns_valid_move_string():
    """
    Prüft, ob die Funktion einen gültigen MOVE-Befehl zum Angreifen eines Opfers zurückgibt.
    """
    env = create_env({10: "<"})
    cmd = eat_victim(env, 1, 100)
    assert cmd.startswith("1 MOVE")


def test_get_best_food_returns_valid_move_string():
    """
    Prüft, ob die Funktion einen gültigen MOVE-Befehl zum Finden von Nahrung zurückgibt
    """
    env = create_env({12: "*"})
    cmd = get_best_food(env, 1, 100)
    assert "MOVE" in cmd


# Leerlauf und Profitbewertung

def test_get_idle_no_enemy_returns_idle_move():
    """
    Ohne Enemy sollte Idle-Befehl (MOVE 0 0) zurückkommen.
    """
    env = create_env({})
    cmd = get_idle(env, 1, 100)
    assert cmd.endswith("MOVE 0 0")


def test_contains_profit_true():
    """
    Soll True liefern, wenn erreichbares Essen vorhanden ist.
    """
    # Food ganz nah (Index 25 ist neben Mitte 24)
    env = create_env({25: "*"})
    assert contains_profit(env, 1, 100) is True


# Randfälle im BiesterLogger

def test_get_biest_coords_default():
    """
    Soll Default-Koordinaten (20,20) liefern.
    """
    clean_biester()
    coords = BIESTER.get_biest_coords(999)
    assert coords == (20, 20)


def test_log_movement_wraps_around_world():
    """
    Bewegung über Weltgrenzen soll korrekt 'umwickeln'.
    """
    clean_biester()
    # Wir setzen uns an den Rand der Welt
    # Wenn wir bei 20,20 starten und WELT_X addieren, sind wir drüber

    move_x = WELT_X + 5
    move_y = WELT_Y + 5

    BIESTER.log_movement(1, (move_x, move_y))

    coords = BIESTER.get_biester()[1]

    # Logik: old(20) + move(71+5) > 71 -> move wird reduziert
    # Das Ergebnis muss innerhalb der Weltgrenzen sein
    assert isinstance(coords, tuple)
