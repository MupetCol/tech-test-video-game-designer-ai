#!/usr/bin/env python3
"""
Hollow Crown — encounter squad tester (limited model).

Runs squad-vs-enemy battles using the same strike rules as simulate.py.
Deliberately ignores range, movement, terrain, healing, and focus-fire tactics.
Each round picks a random living fighter from each side, resolves a duel to
KO (survivor keeps remaining HP), and repeats until one side is eliminated.

    python sim/simulate-encounters.py
    python sim/simulate-encounters.py --trials 1000 --seed 7
"""
import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate import Unit, attack_turn, load_units  # noqa: E402


@dataclass
class Fighter:
    unit: Unit
    hp: int
    side: str  # "player" | "enemy"

    @property
    def alive(self):
        return self.hp > 0


def make_unit(id_, name, cls, attack_type, hp, atk, mag, def_, res, spd, skl, lck):
    return Unit(id_, name, cls, attack_type, hp, atk, mag, def_, res, spd, skl, lck, 0)


ENCOUNTERS = {
    "A": {
        "name": 'Encounter A — "The Sunken Gate"',
        "enemies": [
            ("brigand", "Gate Wretch", "Brigand", "physical", 22, 11, 0, 5, 2, 7, 6, 3),
            ("brigand", "Gate Wretch", "Brigand", "physical", 22, 11, 0, 5, 2, 7, 6, 3),
            ("brigand", "Gate Wretch", "Brigand", "physical", 22, 11, 0, 5, 2, 7, 6, 3),
            ("acolyte", "Bog Acolyte", "Acolyte", "magic", 18, 0, 12, 3, 7, 8, 8, 5),
        ],
    },
    "B": {
        "name": 'Encounter B — "The Hollow Throne"',
        "enemies": [
            ("guard", "Throne Guard", "Knight", "physical", 30, 15, 0, 12, 5, 6, 8, 4),
            ("guard", "Throne Guard", "Knight", "physical", 30, 15, 0, 12, 5, 6, 8, 4),
            ("magus", "Crown Magus", "Battlemage", "magic", 22, 0, 17, 4, 9, 7, 10, 6),
        ],
    },
}

SQUADS = {
    "A": [
        ("Gate Breakers", 19, ["rookwood", "wisp", "brennan"]),
        ("Arcane Rush", 18, ["wisp", "pyraxis", "rookwood"]),
        ("Heavy Door", 19, ["halden", "wisp", "sable"]),
    ],
    "B": [
        ("Split Answer", 19, ["wisp", "rookwood", "brennan"]),
        ("Arcane Battery", 16, ["wisp", "pyraxis", "brennan"]),
        ("Bastion", 20, ["halden", "wisp", "brennan"]),
    ],
}


def spawn_team(units_by_id, ids, side):
    fighters = []
    for i, uid in enumerate(ids):
        u = units_by_id[uid]
        tag = f"{uid}_{i}" if ids.count(uid) > 1 else uid
        fighters.append(Fighter(
            Unit(tag, u.name, u.cls, u.attack_type, u.hp, u.atk, u.mag,
                 u.def_, u.res, u.spd, u.skl, u.lck, u.cost),
            u.hp, side,
        ))
    return fighters


def spawn_enemies(rows):
    fighters = []
    for i, row in enumerate(rows):
        u = make_unit(f"{row[0]}_{i}", row[1], row[2], row[3], *row[4:])
        fighters.append(Fighter(u, u.hp, "enemy"))
    return fighters


def fight(first: Fighter, second: Fighter, rng: random.Random, max_rounds=100):
    """Duel to KO. Survivor keeps remaining HP. Returns (winner, loser)."""
    hp_a, hp_b = first.hp, second.hp
    attacker, defender = first, second
    winner = loser = None
    for _ in range(max_rounds):
        hp_def = attack_turn(attacker.unit, defender.unit,
                             hp_b if defender is second else hp_a, rng)
        if defender is second:
            hp_b = hp_def
        else:
            hp_a = hp_def
        if hp_def <= 0:
            winner, loser = attacker, defender
            break
        attacker, defender = defender, attacker
    else:
        winner, loser = (
            (first, second) if hp_a / first.unit.hp >= hp_b / second.unit.hp
            else (second, first)
        )
    winner.hp = hp_a if winner is first else hp_b
    loser.hp = 0
    return winner, loser


def battle(player_ids, enemy_rows, units_by_id, rng):
    team = spawn_team(units_by_id, player_ids, "player")
    foes = spawn_enemies(enemy_rows)
    pool = team + foes

    while True:
        players = [f for f in pool if f.side == "player" and f.alive]
        enemies = [f for f in pool if f.side == "enemy" and f.alive]
        if not enemies:
            return True
        if not players:
            return False
        a = rng.choice(players)
        b = rng.choice(enemies)
        first, second = (a, b) if rng.random() < 0.5 else (b, a)
        fight(first, second, rng)


def run_encounter(enc_key, units_by_id, trials, rng):
    enc = ENCOUNTERS[enc_key]
    rows = []
    for squad_name, cost, ids in SQUADS[enc_key]:
        wins = sum(
            1 for _ in range(trials)
            if battle(ids, enc["enemies"], units_by_id, rng)
        )
        rows.append((squad_name, cost, 100 * wins / trials))
    return enc["name"], rows


def main():
    ap = argparse.ArgumentParser(description="Hollow Crown encounter squad tester")
    ap.add_argument("--units", default="output/units-rebalanced.csv")
    ap.add_argument("--trials", type=int, default=2000, help="battles per squad")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    roster = load_units(args.units)
    units_by_id = {u.id: u for u in roster}
    rng = random.Random(args.seed)

    print(f"\nHollow Crown — encounter squads  (trials={args.trials}, seed={args.seed})")
    print("Model: random pairwise duels, HP carry-over, no range/mov/healing\n")

    for key in ("A", "B"):
        title, rows = run_encounter(key, units_by_id, args.trials, rng)
        print(title)
        print(f"{'SQUAD':<18}{'COST':>6}{'WIN%':>8}")
        print("-" * 34)
        for name, cost, wr in rows:
            print(f"{name:<18}{cost:>6}{wr:>7.1f}%")
        print()

    print("Limitations: random pairing ignores focus-fire, kiting (range 2),")
    print("healing, and squad positioning. Treat WIN% as a coarse hypothesis check.\n")


if __name__ == "__main__":
    main()
