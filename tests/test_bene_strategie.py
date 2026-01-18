"""
Tests für bene_strategie.py 
"""
import math
import pytest
from pyBiester.bene_strategie import BeastBrain

@pytest.fixture
def brain():
    """
    Erzeugt eine neue Instanz von BeastBrain (n=3) für jeden Test.
    """
    return BeastBrain(n=3)

# Hilfsmethoden Tests

def test_idx_to_pos(brain):
    """
    Prüft, ob die Umwandlung von Index in  Position korrekt funktioniert.
    """
    # Bei size=3: Index 0-8.
    # index 5 ist Zeile 1, Spalte 2
    assert brain.idx_to_pos(5, 3) == (1, 2)
    assert brain.idx_to_pos(0, 3) == (0, 0)
    assert brain.idx_to_pos(8, 3) == (2, 2)

def test_pos_to_move_limits(brain):
    """
    Prüft, ob Bewegungsgrenzen (n=2, da init n=3) eingehalten werden.
    """
    # Tun so, als wären das Biest bei 0,0 und will zu 10,10
    dx, dy = brain.pos_to_move(10, 10, 0, 0)

    # Der Konstruktor setzt self.n = n - 1. Bei n=3 ist self.n also 2.
    assert abs(dx) <= 2
    assert abs(dy) <= 2

def test_dist_calculation(brain):
    """
    Prüft die Distanzberechnung.
    """
    env_size = 3
    i = 8  # Position (2,2)
    # Von (0,0) nach (2,2) -> sqrt(2² + 2²) = sqrt(8) ≈ 2.828
    dist = brain.dist(i, 0, 0, env_size)
    assert math.isclose(dist, 2.828, rel_tol=1e-2)

# Kollisions-Logik

def test_collides_with_relative_true(brain):
    """
    Prüft Kollision, wenn ein Verwandter im Dictionary steht.
    """
    # Biest bei (1,1). Es will nach rechts (dx=1, dy=0) -> Ziel (1,2)
    brain.positions = {
        999: (1, 2) # simulieren, dass ein anderer Bot (ID 999) auf (1,2) steht
    }
    assert brain.collides_with_relative(1, 0, 1, 1) is True

def test_collides_with_relative_false(brain):
    """
    Prüft keine Kollision, wenn das Feld im Dictionary frei ist.
    """
    brain.positions = {
        999: (0, 0) # Bot steht woanders
    }
    # Biest will nach (1,2), dort ist niemand registriert
    assert brain.collides_with_relative(1, 0, 1, 1) is False


# Entscheidungslogik

def test_decide_move_to_food(brain):
    """
    Priorität 3: Futter suchen.
    """
    # Index: 012345678
    env =   ".....*..."  # 5 Punkte, dann Stern (Index 5)

    # my_pos = (1,1). Futter = (1,2). dx=1, dy=0
    result = brain.decide(1, 100, env)

    assert "MOVE" in result
    # Erwartet: Bewegung nach rechts (dx=1, dy=0)
    assert "1 0" in result

def test_decide_flee_from_stronger(brain):
    """
    Priorität 4: Flucht vor Stärkeren.
    """
    # Index: 012345678
    env =   ".....>..." # 5 Punkte, dann Gegner

    result = brain.decide(1, 100, env)
    assert "MOVE" in result

    parts = result.split()
    dx, dy = int(parts[-2]), int(parts[-1])

    # Wenn Gegner rechts (1,0) ist, fliehen wir nach links (-1, 0)
    assert dx == -1 and dy == 0

def test_decide_flee_from_equal(brain):
    """
    Prüft Flucht vor gleichstarkem Gegner.
    """
    # Gegner auf Index 5 (rechts).
    # Kein '>' im Env, damit der 'else'-Zweig im Code genutzt wird.
    env = ".....=..."

    result = brain.decide(1, 100, env)

    assert "MOVE -1 0" in result

def test_decide_chase_weaker(brain):
    """
    Priorität 2: Schwächere jagen.
    """
    # Schwächerer (Index 1)
    # Biest ist auf  (1,1). Ziel ist (0,1). dx=0, dy=-1
    env = ".<......."
    result = brain.decide(1, 100, env)
    assert "MOVE 0 -1" in result

def test_decide_split_when_enough_energy(brain):
    """
    Priorität 1: Split (Genug Energie & sicher).
    """
    env = "........."
    # Code verlangt energy > 50000. Test läuft also mit 50001
    result = brain.decide(1, 50001, env)
    assert "SPLIT" in result

def test_decide_no_split_with_low_energy(brain):
    """
    Kein Split bei zu wenig Energie.
    """
    env = "........."
    # Genau 50000 reicht nicht (da > threshold)
    result = brain.decide(1, 50000, env)
    assert "SPLIT" not in result
    assert "MOVE" in result

def test_decide_stay_when_blocked_by_relative(brain):
    """
    Spezialfall: Weg zum Futter ist durch Verwandten blockiert.
    """
    env = "....*...." # Futter rechts (1,2)

    # manipulieren das Gedächtnis des Bots. Nun steht ein Verwandter auf dem Futter
    brain.positions = {
        2: (1, 2)
    }

    # Da der Weg blockiert ist und keine anderen Trigger vorhanden sind -> Stay (MOVE 0 0)
    result = brain.decide(1, 100, env)
    assert result.endswith("MOVE 0 0")
