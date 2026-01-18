import math


class BeastBrain:
    """Diese Klasse implementiert eine Logik um Biester auf einem Spielfeld zu steuern"""

    FOOD = "*"
    STRONGER = ">"
    EQUAL = "="
    WEAKER = "<"

    treshold = 50_000

    def __init__(self, n=3):  # n=3, da Vorgabe vom Prof
        """Konstruktor"""
        self.n = n - 1  # maximal erlaubte Bewegung in Feldern
        self.my_beasts = set()
        self.positions = {}
        self.split_count = {}

    # --- Hilfsmethoden ---
    def idx_to_pos(self, idx, size):
        """Umwandlung eines Index zu einer Position"""
        # Bsp. idx = 5, size = 3 -> pos(1,2)
        return idx // size, idx % size  # row, col

    def pos_to_move(self, r, c, my_row, my_col):
        """Umwandlung einer Position in einen Bewegungsvektor"""
        dy = max(min(r - my_row, self.n), -self.n)
        dx = max(min(c - my_col, self.n), -self.n)
        return dx, dy  # zuerst dx, dann dy

    def dist(self, i, my_row, my_col, size):
        """Berechnung der Distanz zu einem Ziel"""
        r, c = self.idx_to_pos(i, size)
        # sqrt(a²+b²)=c -> Pythagoras
        return math.sqrt((r - my_row) ** 2 + (c - my_col) ** 2)

    def collides_with_relative(self, dx, dy, my_row, my_col):
        """Zielfeld berechnen und schauen
        ob ein Verwandter auf der Position steht"""
        new_row, new_col = my_row + dy, my_col + dx
        return (new_row, new_col) in self.positions.values()

    def scan_environment(self, env):
        """Das übergebene Environment nach allen möglichen Objekten scannen
        und in einem Dictionary ablegen"""
        data = {
            "food": [],
            "weaker": [],
            "stronger": [],
            "equal": [],
        }
        for i, cell in enumerate(env):
            if cell == self.FOOD:
                data["food"].append(i)
            elif cell == self.WEAKER:
                data["weaker"].append(i)
            elif cell == self.STRONGER:
                data["stronger"].append(i)
            elif cell == self.EQUAL:
                data["equal"].append(i)
        return data

    # --- Entscheidungslogik ---
    def decide(self, beast_id: int, energy: float, env: str) -> str:
        """Die Funktion entscheidet über die nächste Aktion des Biests,
         indem die Prioritäten abgearbeitet werden
        Prioritäten:
        1. Reproduktion wenn Energie > 50_000 und max. 2 mal splitten
        (Logs verfolgen und auf jeweils größten gefressenen Gegner anpassen)
        2. Schwächere Gegner jagen
        3. Futter suchen
        4. Flucht vor gleichstarken oder stärkeren Gegnern
        5. Bewegung zum Zenrum des Spielfelds -> Flächenkontrolle
        6. Stehenbleiben
        """

        self.my_beasts.add(
            beast_id
        )  # Biester anhand der ID eindeutig zum Set hinzufügen
        size = int(math.sqrt(len(env)))
        center = len(env) // 2
        my_row, my_col = center // size, center % size
        self.positions[beast_id] = (
            my_row,
            my_col,
        )  # Position des Biests loggen
        state = self.scan_environment(env)

        # --- 1. Reproduktion ---
        # immer gucken was das stärkste Biest war das wir
        # gegessen haben im letzten Run und ggf. anpassen
        if (
            energy > self.treshold
            # prüfen wie oft gesplittet wurde
            # wenn noch nie dann wert auf 0 setzen
            and self.split_count.get(beast_id, 0) < 2
            and not state["stronger"]
            and not state["equal"]
        ):
            # nur splitten, wenn keine Stärkeren oder Gleichstarken im Sichtfeld
            neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dy, dx in neighbors:
                if 0 <= my_row + dy < size and 0 <= my_col + dx < size:
                    idx = (my_row + dy) * size + (my_col + dx)
                    if (
                        env[idx]
                        in [  # Wenn nix oder Food da liegt
                            ".",
                            self.FOOD,
                        ]  # und kein Verwandter auf dem Feld steht
                        and not self.collides_with_relative(
                            dx, dy, my_row, my_col
                        )
                    ):  # kriegt das Biest dann eine neue ID?
                        # Rückgabe ist die BeastID des aktuellen Biests
                        self.split_count[beast_id] = (
                            self.split_count.get(beast_id, 0) + 1
                        )
                        return f"{beast_id} SPLIT {dx} {dy}"

        # --- 2. Schwächere jagen ---
        if state["weaker"]:
            best = min(  # kürzeste Distzanz berechnen
                state["weaker"],
                key=lambda i: self.dist(i, my_row, my_col, size),
            )
            r, c = self.idx_to_pos(best, size)
            dx, dy = self.pos_to_move(r, c, my_row, my_col)
            if not self.collides_with_relative(dx, dy, my_row, my_col):
                return f"{beast_id} MOVE {dx} {dy}"

        # --- 3. Futter ---
        if state["food"]:
            best = min(
                state["food"], key=lambda i: self.dist(i, my_row, my_col, size)
            )
            r, c = self.idx_to_pos(best, size)
            dx, dy = self.pos_to_move(r, c, my_row, my_col)
            if not self.collides_with_relative(dx, dy, my_row, my_col):
                return f"{beast_id} MOVE {dx} {dy}"

        # --- 4. Flucht vor starken oder gleichstarken Gegnern ---
        if state["stronger"] or state["equal"]:
            target_list = (
                state["stronger"] if state["stronger"] else state["equal"]
            )
            best = min(
                target_list, key=lambda i: self.dist(i, my_row, my_col, size)
            )
            r, c = self.idx_to_pos(best, size)
            dx, dy = self.pos_to_move(r, c, my_row, my_col)
            if not self.collides_with_relative(dx, dy, my_row, my_col):
                return f"{beast_id} MOVE {-dx} {-dy}"

        # --- 5. Bewegung zur Mitte ---
        center_target = size // 2
        dy = max(min(center_target - my_row, 1), -1)
        dx = max(min(center_target - my_col, 1), -1)
        if dx != 0 or dy != 0:
            if not self.collides_with_relative(dx, dy, my_row, my_col):
                return f"{beast_id} MOVE {dx} {dy}"

        # --- 6. STAY ---
        return f"{beast_id} MOVE 0 0"
