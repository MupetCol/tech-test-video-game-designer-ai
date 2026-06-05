# Hollow Crown — Class Counter System (Living GDD)

**System:** v0.3 combat resolution · **Audience:** development team · **Status:** balancing pass

---

## Design intent

Hollow Crown has no separate weapon-triangle UI. Counters emerge from two live rules in `combat-rules.md`: **physical vs. magical damage** (`atk`/`def` vs. `mag`/`res`) and **speed doubling** (a second strike when `attacker.spd − defender.spd ≥ 5`). Each class is a stat profile that makes a unit the right—or wrong—tool for a given threat.

The goal is **situational strength, not universal dominance**. Deployment `cost` prices that flexibility so a budget-20 squad is a set of trade-offs, not a solved lineup. If one unit belongs in every squad, the counter economy has failed.

---

## Rules: how counters form

**Physical vs. magic.** Damage is `max(1, power − defense)`, swapping tracks by `attack_type`. High `def` units are physical sinks; high `res` units are magic sinks. No stat covers both, so mixed enemy squads force mixed answers. This is the primary axis for armored targets: **Throne Guard** (`def` 12, `res` 5) shrugs off physical chip but folds to magic; **Gate Wretch** Brigands (`def` 5, `res` 2) are soft on both, especially magic.

**Speed doubling.** A +5 `spd` edge adds a full extra strike on the attack turn—often more decisive than a few points of `atk`/`mag`. Doubling also feeds accuracy (`hit%` penalizes target `spd`) and crit (`skl`/`lck`). **Myrmidons** are built to cross +5 against slow classes; **Knights** trade tempo for survivability.

**Counterattacks.** Defenders strike back under the same rules. Bulky units create **attrition counters** against glass cannons; fast units that double first create **burst counters**. Class design is choosing which exchange you want to win.

---

## Class roles and situational strength

| Class | Battlefield job | Where it shines | Where it folds |
|---|---|---|---|
| **Knight** | Frontline anchor; holds lanes and body-blocks. | **Encounter A:** walls Brigands (`atk` 11 vs `def` 12). **Encounter B:** pins Throne Guards while allies answer the Magus. | Low `res` → magic magnet. Slow `spd` → doubled. |
| **Soldier** | Flex infantry; stable physical damage and moderate bulk. | Budget filler; reliable vs. soft targets (Brigands, Acolyte `def` 3). | Out-tanked, out-sped, or out-ranged by specialists. |
| **Myrmidon** | Duelist; crosses `spd` thresholds to delete a target. | **Encounter A:** doubles Brigands (`spd` 7). **Encounter B:** doubles Throne Guard (`spd` 6) if it reaches them. | Poor attrition without +5; fragile if engaged on even `spd`. |
| **Archer** | Physical poke at `range` 2. *(Range/mov matter on-map; duel sim ignores them.)* | Chips low-`def` targets (Brigands, Crown Magus `def` 4) before melee commit. | Loses straight trades to fast closers and armored fronts alone. |
| **Cleric** | Magic support at low `cost`; threatens `res`-weak enemies. | **Encounter A:** `mag` 12 into Brigand `res` 2 / Acolyte `res` 7. | Needs a front line; cannot solo high-`res` walls. |
| **Battlemage** | Siege caster; concentrated `mag` vs. high-`def`/low-`res` armor. | **Encounter B:** cracks Throne Guard `res` 5 where physical stalls. | High `cost`, low bulk—dies if reached without anchors. |

---

## Key numbers

**Target win-rate bands** (1v1 duel lens via `simulate.py`—sanity check, not squad play):

| Band | Aggregate duel WR | Meaning |
|---|---|---|
| Core | 45–55% | No trap picks, no auto-includes. |
| Specialist high | 55–70% | Favored stat matchups (magic vs. low `res` armor). |
| Specialist low | 30–45% | Hard counters (slow tank vs. fast doubler). |

Current roster (seed 7, 5000 trials/pair) spans **23–78%**—counter structure works; costs and spreads need tightening toward core.

**Cost ranges by role:** Support caster 4 (Cleric) · Flex physical 5 (Soldier, Archer) · Elite tank 6 (Knight) · Speed duelist 7 (Myrmidon) · Siege caster 9 (Battlemage). Target flat **WIN%/cost** (~9–11%/cost at 50% WR).

**Budget-20 squad templates** (reference encounters, fixed enemies):

*Encounter A — "The Sunken Gate"* (3× Brigand + 1× Acolyte): tests whether multiple squads work, not one auto-include.

- **Bastion + Hex** — Halden (6) + Brennan (5) + Sable (5) + Wisp (4): Knight walls Brigands; Cleric magic hits both `res` profiles.
- **Blitz** — Rookwood (7) + Brennan (5) + Wisp (4) + Sable (5) = 21 → drop Sable: Myrmidon doubles Brigands; magic answers Acolyte.

*Encounter B — "The Hollow Throne"* (2× Knight + 1× Battlemage): `def` wall plus `mag` punch—physical armor alone must not be the universal answer.

- **Armor break** — Halden (6) + Pyraxis (9) + Brennan (5): Battlemage cracks Guard `res` 5; Knight pins; Soldier flexes on Magus.
- **Bastion + Hex** — Halden + Brennan + Sable + Wisp (20): viable but weaker into `res` 9 Magus—proves Encounter B punishes all-round physical lineups.
- **Duelist flanking** — Rookwood (7) + Wisp (4) + Brennan (5) + Halden (6): speed bypass plus magic; no single glass cannon required.

---

## Player experience goal

Before deployment, the player reads the enemy row—armored, casting, fast—and **names the job** each slot fills: anchor, break armor, double a target, poke at range. Winning feels like correct tool choice under 20 points. Losing teaches the counter: physical into Throne Guard grinds; magic without a front line collapses; a slow tank doubled by a Myrmidon dies before it trades back.

The duel sim keeps no class near 80% aggregate; Encounter A/B keep no single unit mandatory in every budget-20 answer.

---

*Living doc — update when `combat-rules.md` or `units.csv` change. Re-verify Encounter A/B templates after each balance pass.*
