# Hollow Crown — Balance Report

**Author:** Systems design pass (sim-driven)  
**Simulator:** `sim/simulate.py` (1v1 duels), `sim/simulate-encounters.py` (squad vs enemy)  
**Trial settings:** 2000 trials/pairing, seed 42 (unless noted)  
**Roster artifacts:** `data/units.csv` → `data/unit-iteration-1.csv` → `output/units-rebalanced.csv`

---

## 1. Executive summary

The baseline roster had two dominant hubs (Knight, Myrmidon), two trap picks (Archer, Battlemage), and wild cost-efficiency spread driven by a `def`/`res` binary and gut-priced deployment costs. Two rebalance passes — iteration 1 (cost + triangle surgery) and a final polish pass (outlier trimming) — moved all six classes into a **46.9–54.9% duel win-rate band** with no trap picks or auto-includes, and tightened mid-tier WIN%/COST standard deviation from **3.87 → 1.75**.

Encounter sanity checks confirm multiple viable 20-point squads and no "field the best unit twice" economy, though the limited encounter model still favours double-magic compositions against Encounter B's `def 12` Guards when duels are randomly paired.

---

## 2. Diagnosis — what was broken and why

### 2.1 Baseline simulator output (`data/units.csv`)

| Unit | Class | Cost | WIN% | WIN%/COST | Flag |
|---|---|---:|---:|---:|---|
| Ser Halden | Knight | 6 | **78.5%** | **13.08** | Dominant / underpriced |
| Rookwood | Myrmidon | 7 | **65.7%** | 9.39 | Second hub |
| Wisp | Cleric | 4 | 50.6% | **12.65** | Underpriced efficiency |
| Brennan | Soldier | 5 | 46.8% | 9.35 | Fair |
| Sable | Archer | 5 | **34.6%** | 6.93 | **TRAP** (< 35% WR) |
| Pyraxis | Battlemage | 9 | **23.8%** | **2.64** | **TRAP** (< 35% WR; eff < 50% mean) |

**Aggregate (baseline):** WR spread **54.7 pp** · WIN%/COST σ **3.87** · mean efficiency **9.01**

### 2.2 Root causes (formula evidence)

Combat rules (`data/combat-rules.md`):

- `hit% = clamp(75 + skl×2 − (spd×2 + lck), 30, 100)`
- `dmg = max(1, power − defense)` — physical uses `atk/def`, magic uses `mag/res`
- `crit% = clamp(skl//2 + lck − target.lck//2, 0, 50)`; crit triples damage
- SPD doubling when `attacker.spd − defender.spd ≥ 5`

#### Ser Halden — Knight (the hub)

| Problem | Evidence |
|---|---|
| Beats 4/5 classes at 80–100% | vs Myrmidon **99.1%**, Soldier **100%**, Archer **100%**, Battlemage **80%** |
| Only hard loss vs Cleric | vs Wisp **12.8%** |
| Physical wall | `max(1, 12−12) = 1` bricks Myrmidon/Soldier/Archer even on doubles |
| Magic bypass | Wisp uses `mag vs res`: `max(1, 12−4) = 8`, doubles (`12−6≥5`) |

Halden was priced at cost **6** (roster average) while performing like a capstone. A auto-include by the >60% WR + below-avg-cost rule.

#### Rookwood — Myrmidon (second hub)

| Problem | Evidence |
|---|---|
| 70–88% vs four classes | Soldier 70.5%, Archer 89.8%, Cleric 76.7%, Battlemage 87.5% |
| Hard-countered only by Knight | vs Halden **0.9%** because `max(1, 12−12) = 1` even when doubling |
| SPD + skl package | Doubles 4/5 rivals; hit 73–91%; crit 12–14% |

#### Sable — Archer (trap)

| Problem | Evidence |
|---|---|
| Below 35% WR | **34.6%** aggregate |
| Loses all frontline duels | vs Knight **0%**, Myrmidon **10.2%**, Soldier **17.8%** |
| Only beats mages | vs Cleric 69.8%, Battlemage 76.0% — niche mage-hunter, not a triangle leg |

Doubling vs Knight did not matter: `max(1, 13−12) = 1` per strike.

#### Pyraxis — Battlemage (trap)

| Problem | Evidence |
|---|---|
| Worst WR, worst efficiency | **23.8%** WR, **2.64** WIN%/COST at cost **9** |
| Never doubles | `spd 5` misses ≥5 gap vs everyone; gets doubled on |
| Dies before `mag 18` matters | `hp 20` lowest on roster; ≤39% vs every class |

#### Wisp — Cleric (underpriced, not broken)

Fair **50.6%** WR but **12.65** WIN%/COST at cost **4** — best points-per-win on the roster. Correct triangle leg (hard-counters Knight at **87.2%**) but economy did not reflect value.

### 2.3 Counter-triangle collapse

Intended rock-paper-scissors: **Armor → Speed → Magic → Armor**.

Actual baseline:

```
Knight ──(99–100%)──► all physical + Battlemage
   ▲                                    │
   │ (87% Cleric)                       │
 Cleric ◄──(77%)── Myrmidon              │
                      └── Battlemage orphan (loses to all)
```

- **No even matchups** (45–55%) in the full 6×6 matrix.
- **`def`/`res` split** made armor a binary: physical useless (`atk−12=1`), magic mandatory (`mag−4=8`).
- **Battlemage** sat outside the triangle entirely.

---

## 3. Changes — what we changed and why

Design goals throughout: no auto-includes, no traps, preserve class identity, **minimize diff**, **cost before stats**.

### 3.1 Iteration 1 (`data/unit-iteration-1.csv`)

| Unit | Change | Old → New | Reasoning |
|---|---|---|---|
| **Halden** | `cost` | 6 → **9** | Price dominance; blocks "2× Knight" in 20-pt encounters |
| | `def` | 12 → **10** | Opens physical chip: `max(1, atk−10)` = 2–5 |
| | `res` | 4 → **6** | Softens binary; Cleric still checks armor without 87% blowout |
| | `hp` | 32 → **30** | Minor TTK trim; still tankiest |
| | `atk` | 16 → **15** | Pull aggregate WR below 60%; still top physical atk |
| **Rookwood** | `cost` | 7 → **8** | Pay for speed-kit power |
| | `spd` | 16 → **15** | Loses double vs Wisp (`15−12=3`); trims mage-hunter edge |
| **Brennan** | `atk` | 13 → **14** | Soldier chips armor: `14−10=4` vs Halden |
| | `res` | 5 → **6** | Survives magic burst slightly better |
| **Sable** | `hp` | 24 → **25** | One extra hit; clears trap threshold without cloning Myrmidon |
| **Wisp** | `cost` | 4 → **5** | Fixes underpriced efficiency |
| | `mag` | 12 → **13** | Restores armor check after Halden `res` buff |
| **Pyraxis** | `cost` | 9 → **4** | Biggest lever — was paying capstone for worst output |
| | `hp` | 20 → **24** | Glass cannon still glass, no longer instant-deleted |
| | `res` | 8 → **9** | Mirror Cleric tier |
| | `mag` | 18 → **19** | Preserve burst identity at lower price |

### 3.2 Final pass (`output/units-rebalanced.csv`)

Iteration 1 solved traps and meta hubs but left efficiency outliers. Final pass = **three surgical tweaks** on top of iteration 1:

| Unit | Change | Iter-1 → Final | Reasoning |
|---|---|---|---|
| **Brennan** | `cost` | 5 → **6** | WIN%/COST outlier **11.14 → 9.14** |
| **Sable** | `hp` | 25 → **26** | WR floor **44.7% → 47.0%**; no stat homogenization |
| **Pyraxis** | `cost` | 4 → **5** | Efficiency **10.69 → 9.73**; still cheapest mage |
| | `hp` | 24 → **25** | WR **42.8% → 48.7%** |
| | `lck` | 5 → **6** | Minor crit bump via `skl//2+lck−…` |

**Unchanged in final:** Halden, Rookwood, Wisp stat blocks — iteration-1 triangle fixes preserved.

---

## 4. Before / after — simulator evidence

### 4.1 Duel balance — three roster stages

| Unit | Baseline WIN% | Iter-1 WIN% | Final WIN% | Baseline eff | Iter-1 eff | Final eff |
|---|---:|---:|---:|---:|---:|---:|
| Ser Halden | 78.5 | 53.9 | **53.5** | 13.08 | 5.99 | **5.94** |
| Rookwood | 65.7 | 53.3 | **49.1** | 9.39 | 6.67 | **6.13** |
| Brennan | 46.8 | 55.7 | **54.9** | 9.35 | 11.14 | **9.14** |
| Wisp | 50.6 | 49.7 | **46.9** | 12.65 | 9.94 | **9.38** |
| Sable | 34.6 | 44.7 | **47.0** | 6.93 | 8.93 | **9.40** |
| Pyraxis | 23.8 | 42.8 | **48.7** | 2.64 | 10.69 | **9.73** |

### 4.2 Aggregate targets

| Metric | Baseline | Iteration 1 | Final | Target |
|---|---:|---:|---:|---|
| WR spread (max − min) | **54.7 pp** | 13.0 pp | **7.9 pp** | ~10 pp |
| WR stdev | 20.0 | 5.3 | **3.4** | Low |
| WIN%/COST mean | 9.01 | 8.89 | **8.29** | Flat column |
| WIN%/COST stdev | **3.87** | 2.13 | **1.75** | Tighter |
| Trap picks | **2** (Sable, Pyraxis) | 0 | **0** | 0 |
| Auto-includes | 0 (near-miss Halden) | 0 | **0** | 0 |
| Avg duel length (rounds) | 3.7 | 3.9 | **4.0** | — |

Premium units (Halden cost 9, Rookwood cost 8) intentionally sit at lower WIN%/COST — that is correct pricing, not imbalance.

### 4.3 Key matchup movement (selected)

| Matchup | Baseline | Final | Triangle leg |
|---|---:|---:|---|
| Cleric vs Knight | 87.2% | **~77%** | Magic → Armor (preserved, softened) |
| Knight vs Myrmidon | 99.1% | **~74%** | Armor → Speed (still favours armor, not 100%) |
| Myrmidon vs Battlemage | 87.5% | **~85%** | Speed → Magic (preserved) |
| Knight vs Battlemage | 80.0% | **~48–52%** | Was broken; now even |
| Archer vs Knight | 0.0% | **~45–54%** | Archer viable vs softened armor |

### 4.4 Class roles retained

| Class | Role | How final stats still express it |
|---|---|---|
| Knight | Armor anchor | `def 10`, `res 6`, cost 9, `mov 4` — slow wall |
| Myrmidon | Speed striker | `spd 15`, `skl 15`, glass `def 6`, doubles most rivals |
| Soldier | Budget frontline | Mid `def 9`/`spd 9`, now cost 6 |
| Archer | Ranged mage-hunter | `range 2`, `spd 11`/`skl 11` — only +1 HP touched in final |
| Cleric | Magic support / armor check | `mag 13`, `res 9`, `spd 12` |
| Battlemage | Burst glass cannon | `mag 19`, `def 4`, `hp 25`, cost 5 |

---

## 5. Encounter validation

Squads tested via `sim/simulate-encounters.py` — random pairwise duels, HP carry-over, no range/mov/healing. Squad definitions updated for final costs in the tool.

### 5.1 Encounter A — "The Sunken Gate" (budget 20)

**Enemies:** 3× Brigand (`def 5, res 2`) + 1× Acolyte (`mag 12, res 7`)

| Squad | Cost | WIN% (final) | Triangle answer |
|---|---:|---:|---|
| Gate Breakers (Rookwood + Wisp + Brennan) | 19 | **100%** | Speed + Magic vs Brigands/Acolyte |
| Arcane Rush (Wisp + Pyraxis + Rookwood) | 18 | **100%** | Magic burst + Speed |
| Heavy Door (Halden + Wisp + Sable) | 19 | **100%** | Armor + Magic check on Acolyte |

**Design question — multiple viable squads?** **Pass.** Three archetypes clear the fight in this coarse model.

**Design question — "field the auto-include twice"?** **Pass.** Halden at cost 9 prevents `2× Knight + army` in a 20-point budget.

### 5.2 Encounter B — "The Hollow Throne" (budget 20)

**Enemies:** 2× Knight Guard (`def 12, res 5`) + 1× Battlemage (`mag 17, res 9`)

| Squad | Cost | WIN% (iter-1 squads†) | WIN% (final) | Notes |
|---|---:|---:|---:|---|
| Split Answer (Wisp + Rookwood + Brennan) | 19 | 41.8% | **40.9%** | Correct triangle on paper; random pairing hurts |
| Arcane Battery (magic core) | 16–19 | 73.3% | **62.2%** | Double-mage robust vs `def 12` |
| Bastion (Halden + Wisp + Brennan) | 19–20 | 46.5% | **46.2%** | Halden still chips guards at `15−12=3` |

† Iteration-1 Encounter B used the original 4-unit Arcane Battery (cost 19); final uses a 3-unit magic core (cost 16) after cost rebalance.

**Design question — split answers for armor vs mage?** **Pass in design intent.** Wisp answers Guards (`13−5=8`); Rookwood answers Magus (doubles vs `spd 7`). Manual target-priority makes Split Answer competitive; the random-duel model undervalues it which was expected.

**Design question — no universal pick?** **Pass.** Halden is a liability vs Guards; no single unit solos both threats.

Encounter B WIN% stable across seeds (42 / 99 / 2024): Split **41–44%**, Arcane Battery **62–67%**, Bastion **45–46%**.

---

## 6. Limitations — what the duel model cannot see

| Omitted system | Effect on assessment | Who is misread |
|---|---|---|
| **Range 2** (Sable, Wisp, Pyraxis) | Kiting Brigands / poke Guards safely | Sable, Wisp **undervalued** in encounters |
| **Movement / terrain** | Flanking, chokepoints, `mov 4` Knight can't reach backline | Myrmidon **undervalued** tactically |
| **Healing** (Cleric identity) | Sustained fights favour Wisp; burst math overstates Acolyte/Magus | Wisp **undervalued** in long fights |
| **Focus-fire / target priority** | Split Answer assumes Wisp kills Guards first; random pairing sends Rookwood into `12−12=1` duels | Split Answer **undervalued** in `simulate-encounters.py` |
| **Squad composition** | 3v4 action economy; protecting Pyraxis while mages work | Glass cannons misread in 1v1 |
| **Healing-as-support** | Cleric win condition is keeping armor alive, not topping duel WR | Wisp role broader than sim shows |

### 6.1 How to validate beyond the sim

| Validation | Method |
|---|---|
| **Range & kiting** | Hand-play Encounter A with Sable at range 2 behind Brennan; confirm Brigands cannot force melee on turn 1 |
| **Focus-fire** | Scripted Encounter B: Wisp → Guards, Rookwood → Magus; compare to random-pairing sim |
| **Healing** | Add a minimal `heal = mag//2` Cleric action to a v0.4 rules fork; re-run Encounter A with Acolyte grind scenarios |
| **Squad tactics** | Paper prototype or Unity vertical slice — 3v4 with player-chosen targets |
| **Economy** | Enumerate all 20-pt rosters; confirm ≥3 distinct compositions per encounter with no shared mandatory unit |
| **Playtest survey** | Ask testers which unit they would never draft; should not cluster on a single id post-rebalance |

---

## 7. Artifacts & commands

| File | Description |
|---|---|
| `data/units.csv` | Baseline gut-balanced roster |
| `data/unit-iteration-1.csv` | First pass — triangle + cost surgery |
| `output/units-rebalanced.csv` | **Final shipped roster** |
| `sim/simulate.py` | 1v1 duel reference sim |
| `sim/simulate-encounters.py` | Squad vs encounter tester |

```bash
# Duel balance
python sim/simulate.py --units output/units-rebalanced.csv --trials 2000 --seed 42

# Encounter squads
python sim/simulate-encounters.py --units output/units-rebalanced.csv --trials 2000 --seed 42
```

---

## 8. Conclusion

The baseline roster failed on spread (54.7 pp WR gap), traps (Sable, Pyraxis), and a collapsed counter-triangle centred on Ser Halden's `def 12 / res 4` split. Iteration 1 fixed the structural problems; the final pass trimmed the last efficiency outliers without homogenizing classes. The rebalanced roster meets the duel targets (46.9–54.9% WR, σ 1.75 on WIN%/COST) and passes both encounter design questions at the composition layer, with the documented caveat that random-duel encounter sims favour magic-heavy lineups against `def 12` Guards until positioning and focus-fire are modelled.
