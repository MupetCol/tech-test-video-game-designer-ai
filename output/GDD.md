# Hollow Crown — Class Counter System (Living GDD)

**System:** v0.3 combat resolution · **Audience:** combat designers · **Status:** rebalanced (`output/units.balanced.csv`)

---

## Design intent

Hollow Crown has no separate weapon-triangle UI. Counters emerge from two live rules in `combat-rules.md`: **physical vs. magical damage** (`atk`/`def` vs. `mag`/`res`) and **speed doubling** (a second strike when `attacker.spd − defender.spd ≥ 5`). Each class is a stat profile that makes a unit the right—or wrong—tool for a given threat.

The goal is **situational strength, not universal dominance**. Deployment `cost` prices that flexibility so a budget-20 squad is a set of trade-offs, not a solved lineup. If one unit belongs in every squad, the counter economy has failed.

---

## Rules: how counters form

**Physical vs. magic.** Damage is `max(1, power − defense)`, swapping tracks by `attack_type`. High `def` units are physical sinks; high `res` units are magic sinks. No stat covers both, so mixed enemy squads force mixed answers. **Throne Guard** (`def 12, res 5`) shrugs off physical chip but folds to magic; **Gate Wretch** Brigands (`def 5, res 2`) are soft on both.

**Speed doubling.** A +5 `spd` edge adds a full extra strike on the attack turn. Doubling also feeds accuracy and crit. **Myrmidons** cross +5 against slow classes; **Knights** trade tempo for survivability.

**Counterattacks.** Defenders strike back under the same rules. Bulky units create **attrition counters** against glass cannons; fast units that double first create **burst counters**.

**Target triangle (post-rebalance):** Armor (Knight/Soldier) ↔ Speed (Myrmidon/Archer) ↔ Magic (Cleric/Battlemage). No class should sit above ~55% aggregate duel WR or below ~45%.

---

## Class roles and situational strength

| Class | Battlefield job | Where it shines | Where it folds |
|---|---|---|---|
| **Knight** | Frontline anchor (`def 10`, cost 9). | **Encounter A:** absorbs Brigand `11 atk`. **Encounter B:** soaks Magus while allies break Guards. | Low `res 6` → magic magnet. `15 atk` only chips Guard `def 12` (`3` dmg). |
| **Soldier** | Flex infantry (cost 6). | Budget frontline; `14 atk` vs soft targets. **Encounter B:** supplemental guard chip. | Out-specialized by Knight, Myrmidon, or mages. |
| **Myrmidon** | Speed duelist (`spd 15`, cost 8). | **Encounter A:** doubles Brigands. **Encounter B:** doubles Crown Magus (`spd 7`). | Random guard duels (`12 atk` vs `def 12` = 1) in squad chaos. |
| **Archer** | Physical poke at `range 2`. *(Sim ignores range.)* | **Encounter A:** chips Brigands/Magus from safety in real play. Mage-hunter in duels. | Loses melee trades vs armor and speed without kiting. |
| **Cleric** | Magic support / armor check (`mag 13`, cost 5). | **Encounter A & B:** `13−res` into Acolyte and Throne Guard `res 5`. Hard-counters Knight in duels. | Needs front line; loses speed war to Myrmidon. |
| **Battlemage** | Burst siege caster (`mag 19`, cost 5). | **Encounter B:** `19−5=14` vs Guard `res` — fastest armor break. | Glass (`def 4`, `hp 25`); dies if focused without anchors. |

---

## Key numbers

**Rebalanced duel results** (`simulate.py`, 2000 trials/pair, seed 42):

| Unit | Cost | WIN% | WIN%/COST |
|---|---:|---:|---:|
| Brennan (Soldier) | 6 | 54.9% | 9.14 |
| Ser Halden (Knight) | 9 | 53.5% | 5.94 |
| Rookwood (Myrmidon) | 8 | 49.1% | 6.13 |
| Pyraxis (Battlemage) | 5 | 48.7% | 9.73 |
| Sable (Archer) | 5 | 47.0% | 9.40 |
| Wisp (Cleric) | 5 | 46.9% | 9.38 |

- **WR spread:** 7.9 pp (46.9–54.9%) — no auto-includes, no trap picks.
- **Mid-tier WIN%/COST:** ~9.1–9.7 (Soldier, Cleric, Archer, Battlemage cluster).
- **Premium pricing:** Knight and Myrmidon intentionally lower WIN%/COST at costs 9 and 8.

**Cost bands (final roster):** Cleric / Archer / Battlemage **5** · Soldier **6** · Myrmidon **8** · Knight **9**.

**Target matchup bands** (duel lens, design targets — not all pairings need to land here):

| Band | Duel WR | Meaning |
|---|---:|---|
| Hard counter | ≥65% | Role counter landed (e.g. Cleric vs Knight). |
| Even | 45–55% | Healthy trade. |
| Bad | ≤35% | Hard-countered specialist. |

---

## Budget-20 squad templates

Validated against `data/encounters.md` design questions; WIN% from `sim/simulate-encounters.py` (random pairing model — see limitations in `BALANCE_REPORT.md`).

### Encounter A — "The Sunken Gate" (3× Brigand + 1× Acolyte)

| Squad | Units (cost) | Role |
|---|---:|---|
| **Gate Breakers** | Rookwood + Wisp + Brennan (**19**) | Speed clears Brigands; Cleric answers Acolyte magic. |
| **Arcane Rush** | Wisp + Pyraxis + Rookwood (**18**) | Magic burst + speed; Pyraxis one-shots Brigands (`19−2`). |
| **Heavy Door** | Halden + Wisp + Sable (**19**) | Knight anchors; magic checks Acolyte; Archer poke (range 2 in real play). |

**Pass:** multiple viable squads; Halden at cost 9 prevents `2× Knight` spam.

### Encounter B — "The Hollow Throne" (2× Guard + 1× Magus)

| Squad | Units (cost) | Role |
|---|---:|---|
| **Split Answer** | Wisp + Rookwood + Brennan (**19**) | Magic breaks Guards; Myrmidon doubles Magus — strong on paper, ~41% in random-duel sim. |
| **Arcane Battery** | Wisp + Pyraxis + Brennan (**16**) | Double magic vs `def 12`/`res 5` Guards; strongest in coarse sim (~62%). |
| **Bastion** | Halden + Wisp + Brennan (**20**) | Wisp carries guard damage; Halden soaks — Halden cannot solo Guards (`15−12=3`). |

**Pass:** no universal pick; physical armor alone fails Guard wall; no solo glass-cannon carry.

---

## Player experience goal

Before deployment, the player reads the enemy row—armored, casting, fast—and **names the job** each slot fills: anchor, break armor, double a target, poke at range. Winning feels like correct tool choice under 20 points. Losing teaches the counter: physical into Throne Guard grinds; magic without a front line collapses; a slow tank doubled by a Myrmidon dies before it trades back.

---

## Sim limitations (GDD scope boundary)

The duel and encounter reference sims **do not model** `range 2` kiting, movement, terrain, healing, or focus-fire. Archer and Cleric are **stronger in real encounters** than random-duel WIN% suggests; Split Answer squads are **undervalued** when Wisp cannot be prioritized onto Guards. Validate squad templates in playtest, not duel WR alone.

---

*Living doc — update when `combat-rules.md` or `output/units.balanced.csv` change. Re-verify squad templates after each balance pass.*
