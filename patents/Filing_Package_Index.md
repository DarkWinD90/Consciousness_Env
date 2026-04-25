# PATENT FILING PACKAGE — CONSOLIDATED INDEX

**Target Filing Date**: TBD (drawings compliance in progress)
**Inventor**: Kevin Christopher Ward
**Three Provisional Applications in Preparation**

---

## Filing Summary

| Patent | Title | Claims | Pages | Key Innovation |
|--------|-------|--------|-------|----------------|
| **A** | Self-Sustaining Neural-Motor Energy Harvesting Loop | 11 claims (2 independent) + 3 Phase 13 supplement claims | ~22 pages | Closed-loop energy: thinking → movement → power → thinking; depth-amortized energy accounting |
| **B** | Configurable Recursive Self-Observation in SNNs | 10 claims (2 independent) + 3 Phase 13 supplement claims | ~17 pages | Tunable self-awareness dial (reflection coefficient 0.0→1.0); inner-iteration self-observation |
| **C** | Cognitive Fallback with Autonomous Self-Regulation | 12 claims (2 independent) + 3 Phase 13 supplement claims | ~20 pages | Continuous intelligent operation during disconnection; depth-aware autonomous runner |

**Total**: 33 base claims + 9 Phase 13 supplement claims = 42 claims across 3 applications (~59 pages). The Phase 13 supplement claims are documented in the per-patent .md files at the bottom and are part of the canonical GitHub specification.

---

## Claim Dependency Map

### Patent A — Energy Loop

```
Claim 1 (Independent — METHOD): General self-sustaining neural-motor-energy loop
├── Claim 3: + thermoelectric harvesting
├── Claim 4: + recursive self-observation (→ Patent B)
│   └── Claim 5: + dynamic reflection coefficient modulation
├── Claim 9: Activity-dependent energy management (quadratic cost model)
├── Claim 11: + STDP learning
└── Claim 14 (Phase 13 supplement): + recurrent-depth inner loop
    with single-charge energy accounting (→ depends on Claims 1, 10)

Claim 2 (Independent — SYSTEM): Hardware system with SNN + actuator + harvester
├── Claim 6: + autonomous fallback controller (→ Patent C)
├── Claim 7: Piezoelectric disc embodiment (27mm on servo shaft)
│   └── Claim 8: + LC resonance with ferrite-backed inductor (Laird)
├── Claim 10: Specific reference design (Pi Pico, servo, piezo disc)
├── Claim 12 (Phase 13 supplement): + inner-loop wrapper running T iterations
│   per outer step; energy store charged exactly once per outer step
└── Claim 13 (Phase 13 supplement): Linear neural compute, constant motor
    harvest scaling property
```

### Patent B — Self-Observation

```
Claim 1 (Independent — METHOD): Recursive self-observation with configurable coefficient
├── Claim 3: Aggregate output = mean membrane potential
├── Claim 4: External cognitive control modulation
├── Claim 5: Internal energy-aware regulation
├── Claim 6: reflection_coeff = base + modulation × sensitivity
├── Claim 7: + STDP self-referential learning loop
├── Claim 8: Single input neuron injection
├── Claim 11 (Phase 13 supplement): + T inner iterations per outer
│   timestep with reflection feedback at each inner iteration
└── Claim 12 (Phase 13 supplement): + cumulative single-charge spike
    accounting per outer timestep across all T inner iterations

Claim 2 (Independent — SYSTEM): SNN system with self-observation components
├── Claim 9: Dual modulation sources (external + internal)
├── Claim 10: Combined with self-sustaining energy loop (→ Patent A)
└── Claim 13 (Phase 13 supplement): + inner-loop controller invoking T
    integrate-and-fire steps with self-observation register update on
    each inner iteration; T dynamically adjustable
```

### Patent C — Cognitive Fallback

```
Claim 1 (Independent — METHOD): Autonomous operation during disconnection
├── Claim 3: 30-second timeout, 5-second polling
├── Claim 4: Four-region energy-aware modulation scheme
├── Claim 5: Periodic state serialization (every 50 steps)
├── Claim 6: Two resync granularity levels (summary vs. full buffer)
├── Claim 7: Hard cap at 10,000 autonomous steps
├── Claim 8: Combined with energy harvesting loop (→ Patent A)
├── Claim 9: Combined with recursive self-observation (→ Patent B)
├── Claim 13 (Phase 13 supplement): + recurrent-depth-enabled SNN driven
│   by autonomous runner with depth parameter T per autonomous step
└── Claim 14 (Phase 13 supplement): + energy-aware selection of T
    (depth-as-energy-modulation-parameter)

Claim 2 (Independent — SYSTEM): Neural processing system with fallback
├── Claim 10: Circadian input generator parameters
├── Claim 11: Crash recovery mechanism
├── Claim 12: Clean shutdown handler
└── Claim 15 (Phase 13 supplement): + recurrent-depth controller
    coupling autonomous input generator to neural processing unit
```

---

## Cross-Patent References

### Interlocking Claims (the "suite lock")

| From | To | Claim | Relationship |
|------|----|-------|-------------|
| Patent A, Claim 4 | Patent B | A depends on B | Energy loop + self-observation |
| Patent A, Claim 6 | Patent C | A depends on C | Energy loop + fallback |
| Patent B, Claim 10 | Patent A | B depends on A | Self-observation + energy loop |
| Patent C, Claim 8 | Patent A | C depends on A | Fallback + energy loop |
| Patent C, Claim 9 | Patent B | C depends on B | Fallback + self-observation |

**Result**: Any complete self-sustaining consciousness loop implementation requires licenses to all three patents. Individual patents can be licensed separately for partial implementations.

---

## Prior Art Differentiation (Consolidated)

| Existing Technology | Patent A | Patent B | Patent C |
|---------------------|----------|----------|----------|
| **Energy harvesting robots** | Harvest from own cognitive-motor activity, not environment | — | — |
| **Neuromorphic chips** (Loihi, TrueNorth) | Close the energy loop (self-powered) | — | — |
| **Recurrent neural networks** | — | Explicit self-observation, not computational feedback | — |
| **Metacognitive AI** | — | Tunable gain on self-referential signal | — |
| **Checkpoint/restart** | — | — | Continuous intelligent operation, not stop-and-restart |
| **Watchdog timers** | — | — | Energy-aware self-regulation, not simple reset |
| **Redundant controllers** | — | — | Single system self-regulation, not duplicate hardware |

---

## Evidence and Validation Summary

### Software Validation (All PASS — 17 Claims)

| Phase | Claims | Status | Reproducible At |
|-------|--------|--------|-----------------|
| Phase 7 Control Baseline | A, B, C, D, E | ALL PASS | `git checkout v0.5.0-phase7-baseline` |
| Phase 7 Full Integration | Energy drain confirmed (control) | CONFIRMED | `git checkout v1.0.0-phase8-stdp` |
| Phase 8 STDP | F8.1, F8.2, F8.3 | ALL PASS | `git checkout v1.0.0-phase8-stdp` |
| Phase 9 Predictive Processing | F9.1, F9.2, F9.3 | ALL PASS | `git checkout v2.0.0-phase9-predictive` |
| Phase 10 Multi-Modal Integration | F10.1, F10.2, F10.3 | ALL PASS | `git checkout v3.0.0-phase10-multimodal` |
| Phase 13 Recurrent Depth | F13.1, F13.2, F13.3 | ALL PASS | `git checkout v4.0.0-phase13-recurrent-depth` (post-merge) |
| MCP Operational | Energy homeostasis at 100 mWh capacity | CONFIRMED | `git checkout v0.6.0-mcp-fallback` |
| Long-Duration Stability | 2,000,000 steps, 7/7 stability checks PASS | CONFIRMED | `main` (latest) |

### Validation Commands

```bash
# Reproduce all validation results from latest validated state
git checkout v4.0.0-phase13-recurrent-depth     # post-merge; pre-merge: branch claude/consciousness-recurrent-structure-KPrLB
python phases/phase7_control_baseline.py          # Claims A-E: ALL PASS
python phases/phase8_stdp.py                      # Claims F8.1-F8.3: ALL PASS
python phases/phase9_predictive_processing.py     # Claims F9.1-F9.3: ALL PASS
python phases/phase10_multimodal.py               # Claims F10.1-F10.3: ALL PASS
python phases/phase13_recurrent_depth.py          # Claims F13.1-F13.3: ALL PASS
```

### Source Code Repository

- **Repository**: https://github.com/DarkWinD90/Consciousness_Env
- **Current validated tag**: v3.0.0-phase10-multimodal (commit 9e2c333); v4.0.0-phase13-recurrent-depth pending merge of `claude/consciousness-recurrent-structure-KPrLB`
- **Total validated claims**: 17 (5 + 3 + 3 + 3 + 3)
- **License**: Proprietary (patent applications in preparation)

---

## Hardware Reduction to Practice (Planned — Phase 11)

**Target completion**: 2026-07-30 (Month 6 of 12)
**Purpose**: Strengthen all three patents with physical evidence

| Component | Specification |
|-----------|--------------|
| Microcontroller | Raspberry Pi Pico (RP2040) |
| Piezoelectric Disc | 27mm |
| Ferrite-backed Inductor | Laird |
| Micro Servo | SG90 9g |
| Thermistor | NTC 10K 3950 |
| Photoresistor | GL5528 LDR |
| RGB LED | WS2812B |

### Hardware Validation Claims (Planned)

| Claim | Criterion | Patent Supported |
|-------|-----------|-----------------|
| F11.1 | Physical energy trajectory matches simulation ±5% | Patent A |
| F11.2 | Spike pattern match >90% | Patent A, B |
| F11.3 | Net-positive energy in hardware | Patent A |

---

## 12-Month Timeline to Non-Provisional

| Month | Milestone | Status |
|-------|-----------|--------|
| **TBD** | File all three provisionals | ⏳ Not filed — drawings compliance in progress |
| 1-3 | Software validation documented, tags created (14 claims across 4 phases) | ✅ COMPLETE |
| 3-6 | Hardware prototype built and validated (Phase 11) | 🔄 PLANNED |
| 6-9 | Hardware results documented (F11.1-F11.3) | ⏳ |
| 9-11 | Non-provisional applications prepared | ⏳ |
| 11-12 | PCT international application filed | ⏳ |
| **12 months after filing** | All three provisionals converted to non-provisional | ⏳ |

---

## Filing Checklist

### For Each Patent Application

- [x] Title of the Invention
- [x] Cross-Reference to Related Applications
- [x] Field of the Invention
- [x] Background (Problem Statement + Prior Art)
- [x] Summary of the Invention
- [x] Detailed Description
- [x] Experimental Validation
- [x] Claims (Independent + Dependent)
- [x] Abstract
- [x] Figure Descriptions
- [x] Source Code Reference
- [ ] **Inventor declaration** (to be signed)
- [ ] **Filing fee payment** (to be submitted)
- [ ] **Patent drawings** (21 figures across 3 patents — 37 CFR 1.84 compliance in progress)
- [ ] **Information Disclosure Statement** (prior art references)

### Post-Filing

- [ ] Receive provisional filing numbers from USPTO
- [ ] Record filing numbers in CLAUDE.md Section 10.2
- [ ] Begin hardware prototype (Month 1-3)
- [ ] Engage patent attorney for non-provisional preparation (Month 6-9)

---

## File Manifest

```
patents/
├── Filing_Package_Index.md          ← THIS FILE
├── Patent_A_Energy_Loop.md          ← Patent A full application + Phase 13 supplement
├── Patent_B_Self_Observation.md     ← Patent B full application + Phase 13 supplement
├── Patent_C_Cognitive_Fallback.md   ← Patent C full application + Phase 13 supplement
├── Energy_Bounded_Recursive_Control_System.txt  ← Reference architecture explanatory doc
└── (future: drawings/, prior_art/)
```

> **Phase 13 supplement note.** Each Patent_X.md file has a clearly-marked
> `## PHASE 13 SUPPLEMENT` section appended at the bottom. The supplement
> claims (3 per patent, totalling 9) were added on 2026-04-25 and are
> part of the canonical GitHub specification.

---

## Important Legal Notes

1. **Provisional patent applications** establish a priority date but do not undergo examination. They must be converted to non-provisional utility patent applications within 12 months to maintain the priority date.

2. **Public disclosure**: After filing, the inventor may publicly disclose the inventions without losing patent rights (in the US). However, international filing (PCT) should be completed before any publication for maximum protection.

3. **Best mode requirement**: The detailed descriptions include the best mode of practicing the invention as currently known to the inventor, including specific parameter values and implementation details.

4. **Enablement requirement**: The source code repository and validation scripts provide sufficient detail for a person skilled in the art to reproduce the invention without undue experimentation.

5. **Patent attorney review**: These provisional applications should be reviewed by a registered patent attorney or agent before conversion to non-provisional applications. The provisional establishes priority; the non-provisional is examined for patentability.

---

*Filing Package in Preparation — patent drawings compliance in progress*
