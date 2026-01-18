import random
from strategy_two import get_action, BIESTER, WELT_X, WELT_Y, Symbol

# --- Kleine Hilfsklasse für das Spielfeld ---
class World:
    def __init__(self, width=WELT_X, height=WELT_Y):
        self.width = width
        self.height = height
        self.grid = {}
        self.beast_id = 1
        self.beast_pos = (20, 20)
        BIESTER.clean()

    def set_symbol(self, x, y, symbol):
        self.grid[(x, y)] = symbol

    def get_symbol(self, x, y):
        return self.grid.get((x % self.width, y % self.height), Symbol.EMPTY.value)

    def get_env(self, radius=3):
        env = []
        bx, by = self.beast_pos
        for dy in range(radius, -radius-1, -1):
            for dx in range(-radius, radius+1):
                env.append(self.get_symbol(bx+dx, by+dy))
        return "".join(env)

    def apply_move(self, move):
        _, _, dx, dy = move.split()
        dx, dy = int(dx), int(dy)
        x, y = self.beast_pos
        self.beast_pos = ((x + dx) % self.width, (y + dy) % self.height)

    def print_world(self):
        print("\n" + "=" * self.width)
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if (x, y) == self.beast_pos:
                    line += "B"
                else:
                    line += self.get_symbol(x, y)
            print(line)
        print("=" * self.width)

# --- Beispielsimulation ---
if __name__ == "__main__":
    world = World()

    # Zufällig Essen und Gegner setzen
    for _ in range(40):
        world.set_symbol(random.randint(0, 70), random.randint(0, 33), Symbol.FOOD.value)
    for _ in range(5):
        world.set_symbol(random.randint(0, 70), random.randint(0, 33), Symbol.ENEMY.value)
    for _ in range(5):
        world.set_symbol(random.randint(0, 70), random.randint(0, 33), Symbol.VICTIM.value)

    print("\nStartposition:")
    world.print_world()

    # 20 Simulationsschritte (kann man variieren)
    for step in range(20):
        print(f"\n=== Schritt {step} ===")

        # Energy in i.d.R. 10 (kann man variieren)
        env = world.get_env(radius=3)
        action, sliced_env = get_action(env, world.beast_id, energy = 10)

        print("Environment:")
        print(sliced_env)
        print("\nAktion:", action)

        world.apply_move(action)
        world.print_world()
