# Hollow Crown — AI-Assisted Balance Workflow

**Assessment artifact:** how AI was used to rebalance the six-unit roster  
**Human role:** systems designer / reviewer — every CSV change was sim-verified before acceptance  
**Plan reference:** Cursor .md plan — used as a menu, not a script

---

## 1. Summary

We used AI as a **fast analyst and pair programmer**, not as an authority on balance. The model produced formula-level diagnoses, triangle maps, stat proposals, and simulator code; the human ran `simulate.py` after every proposal and rejected outputs that looked plausible in prose but failed in numbers.

The delivery plan listed nine phases, nine copy-paste prompts, optional matchup-matrix extensions, three balance iterations, and a fixed file naming scheme (`units.balanced.csv`, `units.iter1.csv`). **We deliberately did not execute that plan linearly.** Several steps were excessive for a six-unit roster, and some plan assumptions (e.g. “Split Answer is the best Encounter B squad”) were wrong once a squad simulator existed. We kept the plan’s *intent* — measure, diagnose, iterate twice, validate encounters, document — and reordered work to stay close to `data/encounters.md` design questions throughout.

---

## 2. Planned flow vs. actual flow

| Plan step | Planned artifact | What we actually did |
|---|---|---|
| Phase 0 — Baseline + matrix | 5000-trial sim, optional `matchup_matrix.py` | Ran `simulate.py` (2000 trials); matrix computed inline during diagnosis prompts — no separate script until later |
| Phase 1 — Diagnosis | Per-unit formula audit | **First major prompt** — full diagnosis table with auto-include/trap flags |
| Phase 2 — GDD | `output/GDD.md` | GDD drafted (ChatGPT-polished prompt from plan Prompt 3); numbers updated after final CSV |
| Phase 3–4 — Iterations 1 & 2 | `units.iter1.csv` + `units.balanced.csv` | `data/unit-iteration-1.csv` then `output/units.balanced.csv`; second pass was three fields, not a full rewrite |
| Phase 5 — Encounter sanity | Manual squad notes | **Encounter squad prompt** + later **`simulate-encounters.py`** — sim contradicted manual squad ranking |
| Phase 6 — Reports | `BALANCE_REPORT.md` | Written after all sims settled |
| Phase 7 — PR | `submission/<name>` branch | Out of scope for this doc |
| Prompt 5 — Sim extension | `matchup_matrix.py` | Skipped as standalone; built **encounter squad sim** instead (higher value for assessment) |
| Prompt 8 — AI mistake doc | Staged failure | Used **real** failures from iteration 1 and encounter sim — see §5 |

**Why we altered the flow**

- **Six units do not need a 2–3 hour, nine-prompt ceremony.** Phases 0, 1, and 4 collapsed into one diagnosis pass with embedded pairwise numbers.
- **Encounter design questions were the north star**, not aggregate duel WR alone. Squad viability for Encounters A/B was checked before calling iteration 1 “done.”
- **We avoided artificial AI errors.** The plan suggested documenting a staged mistake (Prompt 8). We used genuine failures instead — they were more instructive and did not risk shipping bad numbers for documentation’s sake.
- **Manual prompting over batch automation.** Each iteration was a focused Cursor message (“propose iteration 1, run sim”) rather than feeding the model the entire plan checklist at once. That prevented the model from claiming balance before running the sim.

---

## 3. AI tools and why

| Tool | Role | Why this tool |
|---|---|---|
| **Cursor (Agent)** | In-repo execution: run sims, edit CSVs, write `simulate-encounters.py`, produce reports | Has direct access to `sim/`, `data/`, and `output/` — can close the loop “propose → run → read output → revise” in one session |
| **ChatGPT** | Polished prompt drafting for GDD and long-form structure | Better at tightening prose, section outlines, and assessment-ready wording before pasting into Cursor with file attachments |
| **Local prompts (Cursor)** | Diagnosis, iteration, encounter analysis | Kept context tied to exact file contents (`combat-rules.md`, `units.csv`, sim stdout) — minimized hallucinated stat lines |

---

## 4. Concrete prompts and what they produced

Five prompts that materially shaped the delivery (paraphrased from plan templates + thread messages):

### Prompt A — Baseline diagnosis (Plan Prompt 1 · Cursor)

```
You are a tactical RPG systems designer. Here are the combat rules and roster.
The duel sim reports: [simulate.py output].
For each of the 6 units, diagnose WHY their win rate and win%/cost are where they are.
Use exact formulas for hit%, damage, crit%, SPD doubling.
Flag auto-includes and trap picks.
```

**Produced:** Per-unit diagnosis table; identification of Halden as hub (78.5% WR, `def 12` wall), Pyraxis trap (23.8% WR, cost 9), Sable trap (34.6% WR); root cause `def`/`res` binary.  
**Downstream:** Directly fed iteration-1 levers (Halden cost/DEF/RES, Pyraxis cost/HP).

---

### Prompt B — Counter triangle mapping (Plan Prompt 2 · Cursor)

```
Map the 6 classes onto a counter triangle from pairwise duel win rates.
Define hard/soft/even/bad matchups. Where does the roster break the triangle?
What should Encounters A and B reward? Use atk/def/res/spd/skl only.
```

**Produced:** Broken-triangle diagram (Knight + Myrmidon as dual hubs, Battlemage orphan); target Armor → Speed → Magic loop; encounter-specific squad logic.  
**Downstream:** Informed GDD class roles and iteration-1 stat direction (soften Halden wall, price Wisp, rescue Pyraxis).

---

### Prompt C — Iteration 1 rebalance (Plan Prompts 4 + 6 · Cursor)

```
Goals: no auto-include, no traps, preserve class identity, minimize changes.
Prioritize cost before stats. Create unit-iteration-1.csv and run simulate.py.
```

**Produced:** `data/unit-iteration-1.csv`; first sim table (Halden 53.9%, Pyraxis 42.8%, traps cleared).  

---

### Prompt D — Encounter squad viability (Plan Prompt 7 · Cursor, refined after ChatGPT outline)

```
Balanced roster + Encounter A/B enemies, budget 20.
List 3 viable squads per encounter with cost breakdown and triangle rationale.
Flag dominant squads. Note what the duel sim cannot model.
Do we pass the design questions in encounters.md?
```

**Produced:** Nine squads with triangle mapping; “pass” on design questions for iteration-1 roster; explicit limitations (range 2, healing, focus-fire).  
**Downstream:** Hypotheses later tested in `simulate-encounters.py` — some hypotheses failed (§5).

---

### Prompt E — Sim extension + edge-case hunting (adapted from Plan Prompts 5 & 7 · Cursor)

```
Build simulate-encounters.py: random pairwise duels between squad members,
HP carry-over, same combat rules, no range/mov. Show win% per squad.
Run multiple seeds.
```

**Produced:** `sim/simulate-encounters.py`; Encounter A 100% for all squads; Encounter B spread (Split ~42%, Arcane Battery ~73% on seed 42); seed stability check (41–44% vs 62–67% — ranking never flips).  
**Downstream:** Final iteration targeted encounter outliers; `BALANCE_REPORT.md` limitations section; honest ranking of Arcane Battery over Split Answer in the *random-duel* model.

---

### Prompt F — GDD drafting (Plan Prompt 3 · ChatGPT → Cursor)

ChatGPT was used to polish section structure (intent → rules → roles → numbers → PX goal). Cursor then anchored every claim to `combat-rules.md` v0.3 and the final CSV.  
**Produced:** `output/GDD.md` (~2 pages, no new mechanics).

---

## 5. When the AI was wrong — and how we caught it

### Failure 1 — “Split Answer” as the best Encounter B squad (manual analysis)

**AI claim (after Prompt D):** Wisp + Rookwood + Brennan was the **strongest default** for Encounter B — magic answers Guards, speed answers Magus, clean triangle coverage.

**Actual result (`simulate-encounters.py`, seed 42):**

| Squad | WIN% |
|---|---:|
| Split Answer | **41.8%** |
| Arcane Battery | **73.3%** |
| Bastion | 46.5% |

**Why the model failed:** Manual reasoning assumed **focus-fire and target priority** — Wisp kills Guards while Rookwood deletes the Magus. The encounter sim picks **random living fighters** each round, so Rookwood often gets matched into Throne Guards (`max(1, 12−12) = 1` damage) while the Magus free-casts. The model treated squad composition as coordinated play; the tool measured chaotic 1v1s inside a squad fight.

**Fix:** Documented as a sim limitation in `BALANCE_REPORT.md`; ranked Arcane Battery honestly in reports; did not nerf mages just to make the manual narrative true.

---

### Failure 2 — Plan scope vs. assessment needs (process, not numbers)

**Plan assumption:** Linear phases, optional third iteration, staged AI mistake for documentation, `matchup_matrix.py` as highest-value extension.

**Reality:** For six units, encounter squad sim yielded more assessment value than a pairwise matrix script. Staging AI errors would have **misled the balance** for the sake of a workflow doc.

**Human call:** Skip Prompt 8 staging; skip standalone matrix; merge iteration 2 into a small final pass (`output/units.balanced.csv`, three fields changed).

---

## 6. Human review gates (what AI never did alone)

| Gate | Rule |
|---|---|
| **Sim gate** | No CSV promoted without `simulate.py` stdout pasted or re-run |
| **Encounter gate** | Squad claims must survive `simulate-encounters.py` or be flagged as “manual only” |
| **Encounter design gate** | `encounters.md` questions (“multiple viable squads?”, “no universal armor answer?”) checked explicitly |
| **Identity gate** | Reject proposals that homogenize stats (e.g. raising every `atk` to pierce Halden) |
| **Cost-before-stat gate** | Efficiency outliers trimmed with `cost` first (Brennan 5→6, Pyraxis 4→5) |

---

## 7. Scaling to 50+ units, multiple games per quarter

A realistic pipeline for **highly variable per game balancing**, but common skeleton:

### 7.1 Per-game foundation (invest once, reuse)

| Layer | Content |
|---|---|
| **Rules schema** | Machine-readable combat rules (same fields as `combat-rules.md`) versioned per game |
| **Unit schema** | CSV columns + class tags + `attack_type` + deployment cost |
| **Encounter fixtures** | 3–5 reference encounters per game with design questions (like `encounters.md`) |
| **Simulator tier 1** | Duel sim — roster-wide WR / WIN%/COST / pairwise matrix (CI on every PR) |
| **Simulator tier 2** | Encounter sim — squad vs enemy, configurable targeting modes: `random`, `focus-weakest`, `role-priority` |
| **Simulator tier 3** | Gameplay slice — range, mov, healing, terrain stubs; even ugly prototypes beat duel-only for Support/Archer roles |

**Investment priority:** Tier 2+3 is where scaling pays off. Duel-only AI balance does not scale to 50 units because aggregate WR hides composition skills (healers, range, tanks) that encounters actually test.

### 7.2 What stays human

- **Role fantasy** — AI suggests numbers; designers own “Knight means anchor, not DPS”
- **Sim-blind roles** — healers, buffers, pullers: price by encounter utility, document in GDD limitations until Tier 3 sim exists
- **Playtest confirmation** — AI + sim narrow the space; one afternoon of human playtest catches feel issues no formula sees
- **Cross-game judgment** — same AI pipeline, different targets per title (PvP vs PvE, budget size, encounter density)

### 7.3 Throughput estimate

| Roster size | Duel-only AI loop | With encounter + role-priority sim |
|---|---|---|
| 6 units | Hours (this assessment) | +1–2 hours for encounter tool |
| 20 units | 1–2 days | 3–5 days with CI + playtest |
| 50+ units | Unreliable without matrix CI | ~1–2 weeks per game per quarter with shared Tier 2/3 tools |

**Bottom line:** AI scales **analysis and iteration velocity**; simulators scale **trust**. For multiple games per quarter, shared encounter/gameplay sim libraries matter more than better chat prompts.

---

## 8. Artifacts produced via this workflow

| File | AI contribution |
|---|---|
| `data/unit-iteration-1.csv` | AI-proposed; human sim-filtered |
| `output/units.balanced.csv` | AI-proposed final pass; human sim-filtered |
| `output/GDD.md` | ChatGPT structure + Cursor rule anchoring |
| `output/BALANCE_REPORT.md` | Cursor-drafted from sim logs + thread diagnoses |
| `sim/simulate-encounters.py` | Cursor-generated; human-specified model limits |
| `output/DESIGN_AI_WORKFLOW.md` | This document |

---

## 9. Commands to reproduce

```bash
python sim/simulate.py --units output/units.balanced.csv --trials 2000 --seed 42
python sim/simulate-encounters.py --units output/units.balanced.csv --trials 2000 --seed 42
```

**Closing principle:** Treat AI as a **junior systems designer who never runs the build**. The moment sim output contradicts the narrative, the sim wins — and that contradiction is itself a deliverable.
