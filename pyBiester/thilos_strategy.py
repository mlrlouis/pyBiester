import math
from enum import Enum


class BiesterLogger:
    """
    Kuemmert sich um das speichern und verwalten der Biester

    Attributes:
        biester (int: (int,int)): die biester mit id und position gespeichert
    """

    def __init__(self):
        self._biester = {}

    def clean(self):
        """
        entfertn alle biester
        Args:
        Return:
        """
        self._biester = {}

    def get_biest_coords(self, biest_id):
        """
        Gibt die coords des Biest mit der ID biest_id zurück, wenn keine Biest mit
        der ID exestiert dann (-1,-1)
        Args:
            biest_id (int): die ID des biests
        Return:
            (int, int): die Position des biests
        """
        if len(self._biester) == 0:
            return (20, 20)
        return (20, 20)

    def log_movement(self, biest_id, movement):
        """
        Speichert die neue Position des Biestes mit der ID biest_id
        Args:
            biest_id (int): die biest_id des Biests
            movement (int, int): die bewegung des biests relativ zur Position
        """
        coords = self.get_biest_coords(biest_id)
        x, y = movement
        old_coords = (
            self._biester[biest_id] if biest_id in self._biester else coords
        )
        if old_coords[1] + y > WELT_Y:
            y = old_coords[1] + y - WELT_Y
        if old_coords[0] + x > WELT_X:
            x = old_coords[0] + x - WELT_X
        self._biester[biest_id] = tuple(
            a + b for a, b in zip(old_coords, (x, y))
        )

    def get_biester(self):
        """
        gibt das biester dict zurück
        Args:
        Return
            Dict: das biester dict
        """
        return self._biester

    def contains_biest_at_cords(self, cords):
        """
        Gibt wieder ob es ein biest mit den cords gibt
        Args:
            cords (int,int): die coords die überprüft werden sollen
        Return:
            bool: ob es ein biest gibt
        """
        return False


class Symbol(Enum):
    ENEMY = ">"
    VICTIM = "<"
    FOOD = "*"
    EMPTY = "."


# Parameter der Welt:
N = 3
START_ENERGY = 10
FUTTER_ENERGY = 5
SCHRITT_ENERGY = 1
GRUNDUMSATZ = 1
TEIL_ENERGY = 40
WELT_X = 71
WELT_Y = 34

BIESTER = BiesterLogger()


def get_cords(position, biest_id):
    """
    Gibt die  Koordinaten einer Position im enviroment
    Args:
        position (int): die position im enviroment text
        biest_id (int): die ID des biests im mittelpunkt
    Return:
        (int ,int) die Koordinaten auf dem Feld
    """
    biest_cords = BIESTER.get_biest_coords(biest_id)
    y = math.floor((position) / (N * 2 + 1))
    x = position - y * (N * 2 + 1)
    y = N - y
    y = biest_cords[1] + y
    x = x - N
    x = biest_cords[0] + x
    return (x, y)


def get_movement_to_coords(aim_cords, start_cords):
    """
    gibt koordianten relativ für eine bestimmte start koordinate zurück
    Args:
        aim_cords (int ,int): die koordinaten des Ziels
        start_cords (int): die koordinaten des starts
    Return:
        (int, int) die bewegungs koordianten
    """
    distance_x = aim_cords[0] - start_cords[0]
    distance_y = aim_cords[1] - start_cords[1]
    return (distance_x, distance_y)


def get_costs(aim_cords, biest_id):
    """
    gibt die Enegery kosten für eine bestimmte Koordinate
    Args:
        aim_cords (int ,int): die koordinaten des Ziels
        biest_id (int): die ID des biests im mittelpunkt
    Return:
        int die energy kosten für die bewegung
    """
    biest_cords = BIESTER.get_biest_coords(biest_id)
    distance_x = abs(aim_cords[0]) - biest_cords[0]
    distance_y = abs(aim_cords[1]) - biest_cords[1]
    return abs((distance_x * SCHRITT_ENERGY) + (distance_y * SCHRITT_ENERGY))


def get_cheapest_position(enviroment, symbol, biest_id, energy):
    """
    Gibt die Position im enviroment mit der eigenschaft goal zurück die am wenigsten kostet
    Args:
        enviroment (String): die sichtbare Umgebung
        symbol (Symbol): Für welches symbol die kosten bestimmt werden sollen
        biest_id (int): die ID des biests im mittelpunkt
        energy (int): die energy des biests
    Return
        int: die position die am günstigsten ist

    """
    symbol_positions = [
        i for i, c in enumerate(enviroment) if c == symbol.value
    ]
    lowest_costs = N * N * SCHRITT_ENERGY
    cheapest_position = -1
    for position in symbol_positions:
        if get_costs(get_cords(position, biest_id), biest_id) < lowest_costs:
            lowest_costs = get_costs(get_cords(position, biest_id), biest_id)
            cheapest_position = position
    if lowest_costs >= energy:
        return 24
    return cheapest_position


def is_symbol_in_reachable_enviroment(enviroment, symbol, biest_id, energy):
    """
    Ob es ein symbol gibt das innerhalb von einem Zug erreichbar ist werden kann
    Args:
        enviroment (String): die sichtbare Umgebung
        symbol (Symbol): Für welches symbol die kosten bestimmt werden sollen
        biest_id (int): die ID des biests im mittelpunkt
        energy (int): die energy des biests
    Return:
        bool: ob es möglich ist oder nicht
    """
    enviroment = clean_of_not_reachable(enviroment, symbol)
    if symbol.value in enviroment:
        return 24 != get_cheapest_position(
            enviroment, Symbol.VICTIM, biest_id, energy
        )
    else:
        return False


def clean_of_not_reachable(enviroment, symbol):
    """
    entfernt in der Umgebung alle symbols ausser reichweite
    Args:
        enviroment (String): die sichtbare Umgebung
        symbol (Symbol): Für welches symbol die erreichbarkeit  bestimmt werden sollen
    Return:
        String: enviroemnt ohne nicht erreichbare Symbols
    """
    enviroment_list = list(enviroment)
    for i in range(2 * N + 1):
        if enviroment_list[i] is not symbol.value:
            enviroment_list[i] = enviroment_list[i]
        else:
            enviroment_list[i] = Symbol.EMPTY.value
    for i in range(len(enviroment_list) - (2 * N + 1), len(enviroment_list)):
        if enviroment_list[i] is not symbol.value:
            enviroment_list[i] = enviroment_list[i]
        else:
            enviroment_list[i] = Symbol.EMPTY.value
    for i in range(len(enviroment)):
        if i % (2 * N + 1) == 0 or i % (2 * N + 1) == N * 2:
            if enviroment_list[i] is not symbol.value:
                enviroment_list[i] = enviroment_list[i]
            else:
                enviroment_list[i] = Symbol.EMPTY.value
    return "".join(enviroment_list)


def eat_victim(enviroment, biest_id, energy):
    """
    GIbt den String um das nächste Victim zu essen
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des biests im mittelpunkt
        energy (int): die energy des biests
    Return:
        String: der String mit Informationen an den server

    """
    enviroment = clean_of_not_reachable(enviroment, Symbol.VICTIM)
    victim_position = get_cheapest_position(
        enviroment, Symbol.VICTIM, biest_id, energy
    )
    movement_coords = get_movement_to_coords(
        get_cords(victim_position, biest_id),
        BIESTER.get_biest_coords(biest_id),
    )
    BIESTER.log_movement(biest_id, movement_coords)
    return f"{biest_id} MOVE { movement_coords[0]} { movement_coords[1] * (-1)}"


def get_best_food(enviroment, biest_id, energy):
    """
    GIbt den String um das nächste Food zu essen
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des biests im mittelpunkt
        energy (int): die energy des biests
    Return:
        String: der String mit Informationen an den server
    """
    enviroment = clean_of_not_reachable(enviroment, Symbol.FOOD)
    food_position = get_cheapest_position(
        enviroment, Symbol.FOOD, biest_id, energy
    )
    movement_coords = get_movement_to_coords(
        get_cords(food_position, biest_id), BIESTER.get_biest_coords(biest_id)
    )
    BIESTER.log_movement(biest_id, movement_coords)
    return f"{biest_id} MOVE { movement_coords[0]} { movement_coords[1] * (-1)}"


def get_idle(enviroment, biest_id, energy):
    """
    Gibt den String um zu Idlen und ggf zu Flüchten
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des aktuellen biests
        energy (int): die energy des biests
    Return:
        String: der String mit Informationen an den server
    """
    enviroment_list = list(enviroment)
    if Symbol.ENEMY.value in enviroment:
        for position, symbol in enumerate(enviroment_list):
            if symbol != Symbol.ENEMY.value:
                enviroment_list[position] = Symbol.FOOD.value
        enviroment = clean_of_enemy("".join(enviroment_list), biest_id)
        return get_best_food(enviroment, biest_id, energy)
    return f"{biest_id} MOVE 0 0"


def contains_profit(enviroment, biest_id, energy):
    """
    Gibt zurück ob es lohnenstwertes essen in der erreichbaren umgebung gibt
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des aktuellen biests
        energy (int): die energy des biests
    Return
        bool: ob es lohnestwertes essen gibt
    """
    enviroment = clean_of_not_reachable(enviroment, Symbol.FOOD)
    if Symbol.FOOD.value not in enviroment:
        return False
    food_position = get_cheapest_position(
        enviroment, Symbol.FOOD, biest_id, energy
    )
    return (
        get_costs(get_cords(food_position, biest_id), biest_id)
        <= FUTTER_ENERGY
    )


def clean_of_enemy(enviroment, biest_id):
    """
    Gibt das enviroment zurück in dem alles um Enemies essen
    in deren sichtbarem feld entfernt wurden
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des aktuellen biests
    Return
        String: das enviroment ohne und essen im umfeld
    """
    enviroment_list = list(enviroment)
    enemy_positions = [
        i for i, c in enumerate(enviroment) if c == Symbol.ENEMY.value
    ]
    for enemy_position in enemy_positions:
        enemy_coords = get_cords(enemy_position, biest_id)
        for enviroment_position in range(len(enviroment_list)):
            enviroment_coords = get_cords(enviroment_position, biest_id)
            movement_coords = get_movement_to_coords(
                enviroment_coords, enemy_coords
            )
            if (
                abs(movement_coords[0]) <= 2
                and abs(movement_coords[1]) <= 2
                and enviroment_list[enviroment_position] == Symbol.FOOD.value
            ):
                enviroment_list[enviroment_position] = Symbol.EMPTY.value

    return "".join(enviroment_list)


def clean_of_victim_siblings(enviroment, biest_id):
    """
    Gibt das enviroment zurück in dem alle siblings mit kleinerer groesse entfernt wurden
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die ID des aktuellen biests
    Return
        String: das enviroment ohne victim siblings
    """
    victim_positions = [
        i for i, c in enumerate(enviroment) if c == Symbol.VICTIM.value
    ]
    enviroment_list = list(enviroment)
    for position in victim_positions:
        victim_cords = get_cords(position, biest_id)
        if BIESTER.contains_biest_at_cords(victim_cords):
            enviroment_list[position] = Symbol.EMPTY.value
    return "".join(enviroment_list)


def get_action(enviroment, biest_id, energy):
    """
    Handelt nach der "agressiven" strategie und gibt die Handlung zurück
    Args:
        enviroment (String): die sichtbare Umgebung
        biest_id (int): die biest_id des Aktuellen biests
        energy (int): die energy des biests
    Return:
        String die antwort an den Server mit der Handlung
    """
    enviroment = clean_of_victim_siblings(enviroment, biest_id)
    if is_symbol_in_reachable_enviroment(
        enviroment, Symbol.VICTIM, biest_id, energy
    ):
        return eat_victim(enviroment, biest_id, energy), enviroment
    if Symbol.ENEMY.value in enviroment:
        enviroment = clean_of_enemy(enviroment, biest_id)
    if contains_profit(enviroment, biest_id, energy):
        return get_best_food(enviroment, biest_id, energy), enviroment
    return get_idle(enviroment, biest_id, energy), enviroment


def clean_biester():
    """
    leert alle BIESTER die bisher gespeichert wurden
    Args:
        null
    Return:
        null
    """
    BIESTER.clean()


def print_enviroment(enviroment):
    """
    printet das gegebene enviroment in lesbarer formatierung auf die konsole
    Args:
        enviroment (String): die sichtbare Umgebung
    Returns:
    """
    enviroment_list = list(enviroment)
    for i in range(1, round(len(enviroment_list) / (N * 2 + 1))):
        enviroment_list.insert((i * (N * 2 + 1) + i - 1), "\n")
    enviroment_list[math.floor(len(enviroment_list) / 2)] = "B"
    print("".join(enviroment_list))

