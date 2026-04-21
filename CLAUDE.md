# CLAUDE.md — Consciousness_Env System Reference

This document is the institutional memory for every Claude session that touches
this repository.  Read it in full before making any changes.  The design
decisions recorded here are **intentional and load-bearing** — do not "fix"
things that look like bugs without first understanding whether they are
falsifiable controls.

---

## 1. What This System Is

Consciousness_Env is **not a toy, demo, or research curiosity**.  It is the
engineering foundation for a physically deployable, self-sustaining cognitive
loop — an AI system that processes sensory input through a spiking neural
network, drives motor actuation from its neural output, harvests energy from
its own motor activity, observes its own prior computation, and uses that
self-observation to modulate its next decision.

The system is designed to operate inside a physical body or frame — a robot,
prosthetic, drone, sensor node, or any embedded platform with sensors,
actuators, and energy harvesting hardware.  The software in this repository is
the full specification of the signal processing loop.  Every module maps
directly to a physical subsystem.

**Core thesis**: A spiking neural network whose motor output generates
piezoelectric energy sufficient to power the network itself constitutes a
self-sustaining cognitive loop.  Adding recursive self-observation (Layer 8)
makes this loop a candidate for synthetic proto-consciousness — a system that
not only processes information but observes its own processing.

---

## 2. Architecture — The 8-Layer Consciousness Loop

```
                     ENVIRONMENT
                          │
                          ▼
         ┌──────────────────────────────┐
         │  L1: Printed Membrane        │  ThermochromicMixin
         │  L2: Sensing Pads            │  light_intensity, membrane_temp
         └──────┬───────────────────┬───┘
                │ light_intensity   │ membrane_temp
                ▼                   │  (thermal cross-link
         ┌──────────────────────────┐   to L6, below)
         │  L3: Optical Transmission│   │
         │  signal = light/1000*5.0 │   │
         └──────────────┬───────────┘   │
                        │               │
                        ▼               │
         ┌──────────────────────────┐   │
     ┌──►│  L4: Neuromorphic CPU    │   │
     │   │  BaseSNN (leaky I&F)     │   │
     │   │  snn.step(signal,        │   │
     │   │    reflection_coeff)     │   │
     │   └──────────────┬───────────┘   │
     │                  │ snn_output,   │
     │                  │ spike_count   │
     │                  ▼               │
     │   ┌──────────────────────────┐   │
     │   │  L5: Servo Actuation     │   │
     │   │  target_angle =          │   │
     │   │    clip(snn_output*180)  │   │
     │   └──────────────┬───────────┘   │
     │                  │ movement      │
     │                  ▼               ▼
     │   ┌──────────────────────────────┐
     │   │  L6: Energy Harvesting       │
     │   │  harvest: friction + thermal │
     │   │  consume: base + activity(   │
     │   │           spike_count)       │
     │   │  storage: capacity / decay   │
     │   └──────────────┬───────────────┘
     │                  │
     │                  ▼
     │   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
     │      L7: Ground Reference
     │   │  conceptual baseline /      │
     │      noise floor — not a
     │   │  runtime computation stage  │
     │   └ ─ ─ ─ ─ ─ ─ ─┬ ─ ─ ─ ─ ─ ─ ─┘
     │                  │
     │                  ▼
     │   ┌──────────────────────────────┐
     │   │  L8: Recursive Reflection    │
     │   │  prev_mean =                 │
     │   │    membrane_potential.mean() │
     │   │  CLI  coeff = 0.2 (fixed)    │
     │   │  MCP  coeff = 0.2 + mod*0.1  │
     │   └──────────────┬───────────────┘
     │                  │
     └──────────────────┘  ◄── THE LOOP CLOSES AT L4
```

**Three signal pathways:**

| Path | Route | Function |
|------|-------|----------|
| Main spine | L1→L2→L3→L4→L5→L6→L8→L4 | Sense→process→actuate→harvest→reflect→loop. L7 is a conceptual baseline, not a runtime stage. |
| Thermal cross-link | L1 membrane_temp → L6 | Heat from light absorption feeds thermoelectric harvesting directly |
| Reflection feedback | L8 `membrane_potential.mean()` → L4 `snn.step(..., reflection_coeff)` | Self-observation gain differs by execution path: **CLI fixed 0.2** (`phases/phase7_full_integration.py:151`), **MCP `0.2 + modulation * 0.1`** (`mcp/consciousness_mcp_server.py:145`). See Section 3 for per-path parameters. |

**Notes on the diagram:**
- **L6 harvests AND consumes.** The net energy delta is harvest − consume − self-discharge, capped by `capacity_mwh`. Consumption scales with L4 `spike_count` (`core/energy.py` `base_consumption_mw`, `activity_cost_linear`, `activity_cost_quadratic`).
- **L7 is conceptual.** No code computes L7. It is a reference baseline cited in the 8-layer model; the runtime spine skips from L6 to L8.
- **L8 output is the mean membrane potential** across all neurons (`core/base_snn.py:113` `self.previous_output = self.membrane_potential.mean()`), not a dedicated output neuron.
- **Reflection coefficient differs per execution path.** Do not unify the two formulas — the CLI/MCP split is load-bearing (Section 3.3).

---

## 3. Two Execution Paths — And Why Both Exist

### 3.1 CLI Path (phases/phase7_full_integration.py)

| Parameter | Value |
|-----------|-------|
| Neurons | 20 |
| base_consumption_mw | 470.0 |
| friction_factor | 0.0005 |
| thermal_factor | 0.0002 |
| Reflection coeff | Fixed 0.2 |
| Input | sin(t) + noise (hardcoded) |
| Modulation | None |
| Energy at 2000 steps | **-4,697 mWh (dead)** |

### 3.2 MCP Path (mcp/consciousness_mcp_server.py)

| Parameter | Value |
|-----------|-------|
| Neurons | 50 |
| base_consumption_mw | 45.0 |
| friction_factor | 18.0 |
| thermal_factor | 8.0 |
| capacity_mwh | 100.0 (physical storage ceiling) |
| self_discharge_rate | 0.001 per step (0.1% leakage) |
| overflow_thermal_factor | 0.05 °C per mWh overflow |
| Reflection coeff | 0.2 + modulation * 0.1 (variable) |
| Input | Claude-controlled (0-1) |
| Modulation | Claude-controlled (-1 to 1) |
| Energy at 2000 steps | **100.0 mWh (homeostatic equilibrium)** |

### 3.3 THIS IS NOT A BUG — IT IS THE SCIENTIFIC METHOD

Phase 7 full integration **intentionally** uses the harsh EnergyConfig so that
it **fails** the self-charging criterion.  It is the **Section 7.1 falsifiable
control** — the null hypothesis.  The MCP path with BalancedEnergyConfig is the
**alternative hypothesis** — the operational system.

The comparison between the two paths IS the scientific proof:
- Control (CLI): system cannot self-sustain → energy drains to death
- Experimental (MCP): system self-sustains → energy reaches capacity and
  maintains homeostatic equilibrium (excess harvest dissipates as heat)

**Do not "fix" the CLI path's energy config.  Do not merge CLI-path commits
into the MCP-path branch.  The two configurations must remain independent and
comparable.**

### 3.4 The Control Baseline

`phases/phase7_control_baseline.py` runs 2000 steps with canonical parameters
and validates **5 falsifiable claims**:

| Claim | Criterion | Threshold |
|-------|-----------|-----------|
| A | Closed-loop continuity | All channels have 2000 points |
| B | Boundedness | All state variables remain bounded |
| C | Robustness under noise | Std(theta) <= 45 deg, Std(omega) <= 150 |
| D | Input-output gain | corr(L, theta) >= 0.2 |
| E | Saturation ratio | sat_theta <= 0.20 |

Any future change to core physics must re-pass these 5 claims or document why
the claim was revised.

---

## 4. Repository Structure

```
Consciousness_Env/
├── core/                    # Shared physics modules (PACKAGES — have __init__.py)
│   ├── __init__.py          #   Exports: BaseSNN, ThermochromicMixin, EnergyHarvester, etc.
│   ├── base_snn.py          #   Leaky integrate-and-fire SNN with reflection
│   ├── energy.py            #   EnergyConfig, BalancedEnergyConfig, EnergyHarvester
│   ├── thermochromic.py     #   Temperature → color mapping
│   ├── history.py           #   Time-series recorder
│   ├── claude_interface.py  #   ClaudeNeuralInterface
│   ├── neural_router.py     #   ClaudeOptimizedRouter
│   ├── consciousness_enhancer.py
│   ├── enhanced_consciousness.py  # EnhancedConsciousnessSystem
│   ├── predictive.py         #   PredictiveProcessor, PredictiveConfig (Phase 9)
│   └── multimodal.py         #   MultiModalSystem, CrossModalConnector (Phase 10)
│
├── phases/                  # Phase scripts (PACKAGE — has __init__.py)
│   ├── __init__.py
│   ├── phase1_optical_sensing.py
│   ├── phase2_neuromorphic_processing.py
│   ├── phase3_closed_loop_feedback.py
│   ├── phase4_energy_harvesting.py
│   ├── phase5_adaptive_membrane.py
│   ├── phase6_recursive_reflection.py
│   ├── phase7_control_baseline.py    # ◄── 2000-step falsifiable control
│   ├── phase7_full_integration.py    # ◄── 8-layer loop, harsh energy (7.1 control)
│   ├── phase8_stdp.py               # ◄── STDP validation (F8.1-F8.3)
│   ├── phase9_predictive_processing.py  # ◄── Predictive processing (F9.1-F9.3)
│   └── phase10_multimodal.py        # ◄── Multi-modal integration (F10.1-F10.3)
│
├── appendices/              # Supplementary simulations (PACKAGE — has __init__.py)
│   ├── __init__.py
│   ├── appendix_a_base_simulation.py
│   ├── appendix_b_system_graph.py
│   └── appendix_c_recursive_reflection.py
│
├── mcp/                     # MCP servers (PACKAGE — has __init__.py)
│   ├── __init__.py
│   ├── consciousness_mcp_server.py   # ◄── Physics + SNN + fallback (v1.1.0)
│   ├── consciousness_server.py       # ◄── Cognitive layer (stateless reasoning)
│   ├── mcp-config.json
│   └── .snapshots/                   # Fallback state snapshots (gitignored, created at runtime)
│
├── tools/                   # Utilities (PACKAGE — has __init__.py)
│   ├── __init__.py
│   ├── code_simplifier.py           #   Code analysis / simplification
│   ├── collision_checker.py          #   SVG element collision detection
│   ├── enhanced_collision_checker.py #   Pixel-level collision validation
│   ├── svg_audit.py                  #   SVG structure auditor
│   ├── run_uspto_compliance_audit.py #   Full USPTO compliance runner
│   ├── run_collision_check.py        #   Geometric collision auditor (text/line/numeral)
│   ├── audit_arrow_endpoints.py      #   Arrow endpoint distance auditor
│   ├── verify_signal_paths.py        #   Signal path + numeral-path collision checker
│   ├── fix_numeral_collisions.py     #   Batch numeral position fixer
│   ├── fix_arrow_endpoints_v2.py     #   Arrow endpoint adjuster
│   └── google_drive.py              #   Google Drive API utility (optional)
│
├── tests/                   # Test suite (PACKAGE — has __init__.py)
│   ├── __init__.py
│   ├── run_200_step_test.py          #   2000-step MCP integration test (standalone)
│   ├── run_stress_test.py            #   10,000-step stability test (standalone)
│   ├── run_soak_test.py              #   2,000,000-step endurance test (standalone)
│   ├── test_code_simplifier.py       #   pytest: code analyzer tests
│   ├── test_line_thickness_validator.py  #   pytest: SVG stroke width validation
│   ├── test_patent_diagram_regressions.py  #  pytest: patent drawing structure
│   ├── test_phase7_metrics.py        #   pytest: Phase 7 claim validation
│   └── test_reference_validator.py   #   pytest: reference numeral validation
│
├── patent_drawings/         # USPTO-compliant SVG drawings (37 CFR 1.84)
│   ├── patent_a/            #   Patent A: 8 figures (fig1-fig8.svg)
│   ├── patent_b/            #   Patent B: 6 figures (fig1-fig6.svg)
│   ├── patent_c/            #   Patent C: 7 figures (fig1-fig7.svg)
│   ├── compliance_runs/     #   Timestamped compliance audit logs
│   ├── FINDINGS_REPORT.md
│   ├── NUMERAL_REGISTRY.md
│   ├── USPTO_COMPLIANCE_CROSS_REFERENCE.md
│   └── USPTO_Compliance_Report.md
│
├── patents/                 # Patent specifications and filing materials
│   ├── Patent_A_Energy_Loop.md
│   ├── Patent_B_Self_Observation.md
│   ├── Patent_C_Cognitive_Fallback.md
│   ├── Filing_Package_Index.md
│   ├── Energy_Bounded_Recursive_Control_System.txt
│   ├── forms/               #   USPTO blank forms (SB15A, SB16)
│   ├── pdfs/                #   Generated filing PDFs (12 files, 4 per patent)
│   └── uspto_formatted/     #   USPTO-formatted text specs + filing instructions
│
├── docs/                    # Documentation
│   ├── brutal_reality_check.md
│   ├── phase7_control_baseline.md
│   ├── reference_architecture.txt
│   └── hardware/            #   Phase 11 hardware specs and BOM
│
├── .github/workflows/       # CI/CD pipelines
│   ├── python-app.yml       #   Primary CI: lint + pytest + phase validations
│   ├── python-package-conda.yml  #   Conda: lint + pytest only
│   └── python-publish.yml   #   PyPI publishing
│
├── consciousness_cli.py     # CLI entry point: `consciousness run|appendix|version`
├── export_specifications_pdf.py  # Patent spec → PDF (37 CFR 1.52 compliant)
├── fill_patent_forms.py     # USPTO form filler (SB16, SB15A)
├── setup.py                 # Package config (find_packages + py_modules)
├── MANIFEST.in              # Source distribution includes
├── requirements.txt
├── environment.yml          # Conda environment config
├── .mcp.json                # MCP server configuration
├── 2026-02-02_Patent_Filing_Summary.md
└── CLAUDE.md                # THIS FILE
```

### Critical: __init__.py files are load-bearing

`appendices/`, `phases/`, and `mcp/` all have `__init__.py` files so that
`find_packages()` in `setup.py` discovers them.  Without these files, pip/wheel
installs exclude those directories entirely and the CLI raises
`FileNotFoundError`.  Do not remove them.

---

## 5. MCP Servers — The Cognitive Architecture

Two MCP servers work together, bridged by Claude:

### 5.1 consciousness (consciousness_mcp_server.py)

**Owns the physics.**  Contains the SNN, energy harvester, thermochromic mixin,
and the full simulation loop.  Claude drives it step-by-step.

Tools: `initialize_consciousness`, `step_simulation`, `get_neural_state`,
`get_system_status`, `apply_cognitive_response`, `set_goal`, `set_stimuli`,
`get_attention_needs`, `get_history`, `get_fallback_status`, `resync`

### 5.2 consciousness-cognitive (consciousness_server.py)

**Pure reasoning layer.**  No neurons, no physics.  Takes state descriptions
and returns cognitive decisions: modulation values, attention allocation,
intention formation.

Tools: `cognitive_query`, `form_intention`, `allocate_attention`

### 5.3 The Bridge Pattern

```
Claude reads from consciousness-cognitive:
    "What should I do given these conditions?"
    → Returns: modulation=-0.2, action="conserve energy"

Claude writes to consciousness:
    apply_cognitive_response(modulation=-0.2)
    → Applied to SNN on next step_simulation() call
```

Claude is the cognitive bridge.  Server 2 reasons; Server 1 executes.

---

## 6. Autonomous Fallback System (v1.1.0)

When Claude (the cognitive layer) goes silent for >30 seconds, the system does
not stop.  It enters autonomous fallback mode.

### 6.1 How It Works

1. **Heartbeat watchdog** checks every 5s whether a tool call has arrived
2. If 30s elapse with no activity → `AutonomousRunner` engages
3. Runner steps the SNN with a self-regulating input generator:
   - Circadian-like sinusoidal base signal
   - 10% chance of random attention burst per step
   - Energy-aware modulation:
     - `<15 mWh` → modulation -0.4 (conserve)
     - `<30 mWh` → modulation -0.1 (cautious)
     - `>80 mWh` → modulation +0.3 (spend surplus)
     - else → 0.0 (neutral)
4. Every step is buffered for resync
5. Every 50 steps → state snapshot to `mcp/.snapshots/latest.json`
6. Hard cap at 10,000 autonomous steps

### 6.2 Recovery Scenarios

| Scenario | Recovery |
|----------|----------|
| Claude goes quiet >30s | Watchdog engages fallback. On reconnect, `resync` returns buffered history. |
| MCP server crashes | On restart, `initialize_consciousness` restores from `latest.json` snapshot. |
| Clean shutdown (stdin EOF) | `finally` block writes shutdown snapshot. |

### 6.3 Resync Payload

When Claude reconnects and calls `resync`, it receives:
- `steps_autonomous`: how many steps ran without cognitive input
- `energy_delta`: net energy change during fallback
- `summary`: min/max/mean energy and spikes
- `full_buffer` (optional): every step's input, modulation, spikes, energy, temp, pattern

---

## 7. Git Workflow — Tags, Branches, and Forward Progress

### 7.1 Core Principles

1. **`main` is the advancing frontier.**  Every commit on `main` has passed
   all prior phase validations.  It is always the latest "known good" state.
2. **Tags are the scientific record.**  Annotated tags mark validated
   milestones.  Tags are immutable — they pin a commit hash forever.
3. **Feature branches are workspaces.**  `claude/*` branches are where work
   happens.  Once merged to `main` via PR, the branch stays on GitHub as a
   read-only audit trail.  Never commit to a merged branch again.
4. **Validation scripts are frozen.**  Once a phase's validation script is
   merged, it is never modified.  New phases get new scripts.

### 7.2 Version Tags — The Milestone Registry

Tags use semantic versioning: `vMAJOR.MINOR.PATCH-label`.  Major version
increments when a new phase with falsifiable claims is validated.

```
v0.1.0-architecture      52cca38  Initial 8-layer architecture
v0.2.0-energy-physics    1fa4488  Energy physics corrected
v0.3.0-balanced-energy   f76ffe8  BalancedEnergyConfig (experimental hypothesis)
v0.4.0-mcp-servers       da842a6  MCP physics server operational
v0.5.0-phase7-baseline   7c369d8  Phase 7 claims A-E established
v0.6.0-mcp-fallback      307c5f6  Autonomous fallback v1.1.0
v0.7.0-package-fix       517bd26  Package install fix
v1.0.0-phase8-stdp       80cf3e5  Phase 8 STDP (F8.1-F8.3 PASS + regression PASS)
v2.0.0-phase9-predictive 4baa21f  Phase 9 Predictive Processing (F9.1-F9.3 PASS + regression PASS)
v3.0.0-phase10-multimodal 9e2c333  Phase 10 Multi-Modal Integration (F10.1-F10.3 PASS + regression PASS)
```

**Reproduce any validated state:**
```bash
git checkout v0.5.0-phase7-baseline   # exact Phase 7 state
git checkout v1.0.0-phase8-stdp       # exact Phase 8 state
```

### 7.3 New Phase Workflow (Step-by-Step)

This is the concrete procedure for adding any new phase (e.g., Phase 9):

```
1. START FROM MAIN
   git checkout main && git pull origin main

2. CREATE FEATURE BRANCH
   git checkout -b claude/phase9-predictive-processing-<session-id>

3. IMPLEMENT
   - Add core logic to core/ (if shared) or phases/ (if phase-specific)
   - Write phases/phase9_predictive.py with falsifiable claims
   - Each claim: explicit threshold, prints PASS or FAIL, never silent

4. VALIDATE — RUN ALL PRIOR PHASES + NEW PHASE
   python phases/phase7_control_baseline.py    # Claims A-E must PASS
   python phases/phase8_stdp.py                # Claims F8.1-F8.3 must PASS
   python phases/phase9_predictive.py          # Claims F9.1-F9.3 must PASS

5. COMMIT WITH VALIDATION RESULTS IN MESSAGE
   git add <specific files>
   git commit -m "Phase 9: Predictive processing — F9.1-F9.3 PASS

   Regression: Phase 7 A-E PASS, Phase 8 F8.1-F8.3 PASS"

6. PUSH AND OPEN PR
   git push -u origin claude/phase9-predictive-processing-<session-id>
   gh pr create --title "Phase 9: Predictive Processing" ...

7. AFTER MERGE — TAG THE MILESTONE
   git checkout main && git pull origin main
   git tag -a v2.0.0-phase9-predictive <hash> -m "Phase 9: Predictive Processing
   - F9.1 PASS: Prediction error decreases >50% over 10 cycles
   - F9.2 PASS: Random input shows no decrease (p > 0.05)
   - F9.3 PASS: Error recovers within 200 steps after frequency switch
   - Regression: Phase 7 A-E PASS, Phase 8 F8.1-F8.3 PASS"
   git push origin --tags
```

### 7.4 Regression Validation Rule

**Before any PR is merged to `main`, ALL prior phase validation scripts must
PASS.**  This is non-negotiable.  The validation commands to run:

```bash
python phases/phase7_control_baseline.py          # Claims A-E
python phases/phase8_stdp.py                      # Claims F8.1-F8.3
python phases/phase9_predictive_processing.py     # Claims F9.1-F9.3
python phases/phase10_multimodal.py               # Claims F10.1-F10.3
# ... add each new phase script as phases are added
```

If a new phase breaks a prior validation:
- **Do not modify the prior validation script**
- Fix the new code until all validations pass
- If the prior claim is genuinely obsoleted, document why in the new phase
  script and in the commit message — but the old script stays unchanged

### 7.5 Branch Lifecycle

```
Feature branch created → Work committed → PR opened → Validated → Merged
    │                                                              │
    │                                                              ▼
    │                                                    Tag created on main
    │
    └── Branch stays on GitHub as read-only audit trail
        (never deleted, never committed to again)
```

### 7.6 What NOT To Do

- **Don't avoid merging to `main`.**  Main must advance.  Reproducibility
  comes from tags and commit hashes, not from branch isolation.
- **Don't modify old validation scripts.**  Write new ones.
- **Don't merge without running ALL prior validations.**
- **Don't delete `claude/*` branches.**  They are the audit trail of how
  each piece of work was developed.
- **Don't tag unvalidated states.**  Tags mean "all claims PASS at this point."

### 7.7 Handoff Protocol for Claude Sessions

Each Claude session that modifies this repo should:

1. **Read CLAUDE.md first** — understand what exists and what is frozen
2. **Fetch everything** — `git fetch origin --tags` to sync remote state
3. **Check tags** — `git tag -l -n1` shows the current milestone registry
4. **Check main** — `git log --oneline -10 origin/main` to see recent history
5. **Compare tags to Section 7.2** — if the tags already exist on the remote,
   DO NOT recreate them.  If `git tag -l` returns the tags listed in Section
   7.2, the milestone registry is already set up.  Move on.
6. **Branch from `main`** — not from another `claude/*` branch
7. **Run all validations before committing** — record results in commit msg
8. **Update Section 7.2** of this file if a new tag is created
9. **Update Section 9** of this file if a new phase is completed

**CRITICAL**: Always `git fetch origin --tags` BEFORE checking tags.  Without
this fetch, a fresh session may not see tags that exist on the remote and will
incorrectly conclude they need to be created.  The fetch is non-negotiable.

This ensures continuity across sessions.  A new Claude instance can reconstruct
the full project state from tags alone:
```bash
git fetch origin --tags         # ALWAYS fetch first
git tag -l -n1                  # See all milestones
git log v1.0.0-phase8-stdp     # See history up to Phase 8
git checkout v1.0.0-phase8-stdp  # Reproduce Phase 8 exactly
```

---

## 8. Scientific Methodology — The Falsifiable Framework

Every phase of this system follows the same pattern:

1. **State the claim** in code as a validation function with explicit thresholds
2. **Build the control** — a configuration that is designed to FAIL the claim
3. **Build the experiment** — a configuration that is designed to PASS the claim
4. **Run both** and record the results
5. **Tag the validated state** on `main` so it is permanently reproducible
6. **Advance only when all prior claims still pass** (regression validation)

This is not optional process.  It is the engineering methodology that makes
this system trustworthy for physical deployment.  A self-sustaining cognitive
loop that goes into a robot must be provably correct.  "It seems to work" is
not sufficient.  "Here is the proof it fails without X, and here is the proof
it succeeds with X" is sufficient.

**The two energy configs (EnergyConfig vs BalancedEnergyConfig) must remain
independent.**  Both live in `core/energy.py`.  The control baseline always
uses the harsh config.  The operational system uses the balanced config.  This
separation is enforced by the validation scripts, not by branch isolation.

---

## 9. Forward Roadmap — Next Phases

### Phase 8: Synaptic Plasticity (STDP) — COMPLETE

**Objective**: Enable the SNN to learn from temporal correlations without
external training.  Spike-Timing Dependent Plasticity strengthens connections
between neurons that fire in causal sequence and weakens connections between
neurons that fire in anti-causal sequence.

**Implementation** (core/base_snn.py):
- Trace-based STDP via `_stdp_update()` method in BaseSNN
- Pre/post eligibility traces decay exponentially (τ=20 steps), increment on spike
- LTP: w[i,j] += A+ × pre_trace[i] when post neuron j fires
- LTD: w[i,j] -= A- × post_trace[j] when pre neuron i fires
- A- > A+ (depression slightly stronger) prevents runaway excitation
- Weight bounds [w_min, w_max] enforced; self-connections zeroed each step
- Opt-in via `stdp_enabled=True` in SNNConfig — all prior phases unaffected

**New SNNConfig parameters**:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `stdp_enabled` | `False` | Opt-in toggle — existing code unchanged |
| `a_plus` | `0.01` | LTP amplitude (potentiation strength) |
| `a_minus` | `0.012` | LTD amplitude (depression strength, >A+ for stability) |
| `tau_plus` | `20.0` | LTP trace time constant (steps) |
| `tau_minus` | `20.0` | LTD trace time constant (steps) |
| `w_min` | `0.0` | Minimum synaptic weight bound |
| `w_max` | `0.5` | Maximum synaptic weight bound |

**Validation parameters** (phases/phase8_stdp.py):

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `threshold` | `0.3` | Lower than default (0.5) to enable cascading downstream spikes |
| `weight_scale` | `0.2` | Higher than default (0.1) so propagated spikes reach threshold |
| `input_scale` | `1.0` | Full-strength input drive |
| `a_plus` | `0.005` | Moderate learning rate (prevents saturation at w_max) |
| `a_minus` | `0.006` | 1.2:1 LTD/LTP ratio preserved |
| `N_STEPS` | `1000` | 5 full input cycles (period=200) |
| `SEED` | `42` | Reproducible |

**Falsifiable claims — ALL PASS**:

| Claim | Criterion | Measured | Threshold | Result |
|-------|-----------|----------|-----------|--------|
| F8.1 | Weight entropy decreases | 2.9546 → 2.0151 bits (Δ = 0.9395) | final < initial | **PASS** |
| F8.2 | STDP MI > 1.2× frozen MI | 0.1016 / 0.0156 = 6.52× | ratio > 1.20 | **PASS** |
| F8.3 | Late weight Δ < 10% of early Δ | 0.0000 / 1.3051 = 0.00% | ratio < 0.10 | **PASS** |

**Control**: Same network with `stdp_enabled=False` (frozen weights), same
input sequence, same random seed.  Identical initial conditions.

**Phase 7 regression**: All 5 control baseline claims (A-E) still PASS after
STDP changes to BaseSNN.  STDP is opt-in (`stdp_enabled=False` by default),
so the existing step() pipeline is unchanged when STDP is disabled.

**Key insight from validation**: The default BaseSNN parameters (threshold=0.5,
weight_scale=0.1) produce only single-neuron spiking — insufficient cascading
activity for STDP to operate.  The validation script uses threshold=0.3 and
weight_scale=0.2, which creates multi-neuron cascade dynamics where ~70% of
downstream neurons reach firing threshold from propagated spikes.  This is not
a bug in STDP — it is a parameter regime requirement.  STDP needs multi-neuron
activity to detect temporal correlations.

---

### Phase 9: Predictive Processing — COMPLETE

**Objective**: The system predicts its own next input before it arrives.
Prediction error becomes a learning signal.

**Implementation** (core/predictive.py):
- Dual pathway: Predictor SNN (STDP-enabled) and Processor SNN (frozen)
- Both SNNs receive the actual input signal at each step
- Predictor drives a temporal feature buffer (rolling window of mean membrane potential)
- Linear readout maps feature buffer → predicted next input
- Delta rule adjusts readout weights from signed prediction error
- Weight decay (0.999/step) prevents explosion and enables re-adaptation
- `PredictiveProcessor` class wraps both SNNs + readout in one interface
- `get_prediction_error_modulation()` converts error to consciousness loop modulation

**Key design decision**: The system predicts the **next input signal**, not
the processor output.  Processor output has high autocorrelation (~0.93) for
both periodic and random input due to refractory dynamics.  Predicting the
raw input ensures periodic input is learnable (F9.1 passes) while random
input is genuinely unpredictable (F9.2 passes).

**New classes** (core/predictive.py):

| Class | Purpose |
|-------|---------|
| `PredictiveConfig` | Dataclass: SNN params + readout params (buffer, lr, decay) |
| `PredictiveProcessor` | Dual-pathway system: processor SNN + predictor SNN + readout |

**Validation parameters** (phases/phase9_predictive_processing.py):

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `threshold` | `0.5` | Default — produces autocorrelation asymmetry |
| `weight_scale` | `0.1` | Default — sparse cascading sufficient for temporal features |
| `input_scale` | `0.8` | Default — strong input drive |
| `a_plus` | `0.005` | Same as Phase 8 — moderate STDP learning |
| `a_minus` | `0.006` | 1.2:1 LTD/LTP ratio preserved |
| `BUFFER_LEN` | `100` | Half input period — captures phase information |
| `READOUT_LR` | `0.05` | Balances F9.1 learning speed and F9.2 stability |
| `WEIGHT_DECAY` | `0.999` | Prevents weight explosion, enables F9.3 re-adaptation |
| `N_STEPS` | `2000` | 10 full input cycles (period=200) |
| `PERIOD_2` | `100` | Half original — clear frequency change for F9.3 |
| `SWITCH_STEP` | `1000` | Midpoint — 5 cycles to learn, then switch |
| `SEED` | `42` | Reproducible |

**Falsifiable claims — ALL PASS**:

| Claim | Criterion | Measured | Threshold | Result |
|-------|-----------|----------|-----------|--------|
| F9.1 | Prediction error reduction cycle 1→10 | 63.9% | >50% | **PASS** |
| F9.2 | Random input trend p-value | 0.6919 | >0.05 | **PASS** |
| F9.3a | Error spike after frequency switch | 1.51× pre-switch | >1.3× | **PASS** |
| F9.3b | Error recovery after spike | recovery < peak | recovery < peak | **PASS** |

**Control**: Same dual-pathway system with `learning_enabled=False` (frozen
readout weights, STDP disabled).  Control prediction stays at initial bias
(0.5) — no error reduction.

**Phase 7 regression**: All 5 control baseline claims (A-E) still PASS.
Phase 9 does not modify `core/base_snn.py` — it creates independent
`BaseSNN` instances with standard configuration.

**Phase 8 regression**: All 3 STDP claims (F8.1-F8.3) still PASS.
Phase 9 code is purely additive (new module + new validation script).

---

### Phase 10: Multi-Modal Sensory Integration — COMPLETE

**Objective**: Process multiple sensor modalities (light, sound, pressure)
through separate SNN populations and bind them through cross-modal spike
synchronization.  Cross-modal connections learn via STDP.

**Implementation** (core/multimodal.py):
- Three independent BaseSNN instances (one per modality: light, sound, pressure)
- CrossModalConnector manages 6 cross-modal weight matrices (bidirectional
  connections for each of 3 pairs: L↔S, L↔P, S↔P)
- Broadcast input injection: input drives ALL neurons in each population
  (not just neuron 0) so that population-level spike timing depends on
  input phase — critical for synchronization differentiation
- Cross-modal STDP uses same trace-based algorithm as BaseSNN._stdp_update()
  but implemented independently in the connector (no changes to base_snn.py)
- Within-modality STDP disabled to isolate cross-modal learning effect
- MultiModalSystem wraps all components into a single step() interface

**Key design decisions**:

1. **Input-driven regime**: threshold=0.8, weight_scale=0.05 (vs Phase 8's
   0.3/0.2). In the Phase 8 regime, recurrent dynamics dominate and spike
   patterns are identical regardless of input phase.  The higher threshold
   ensures neurons only fire when input signal is strong, making spike
   timing genuinely input-dependent.

2. **Broadcast input**: Input is added to ALL neurons' membrane potentials
   (not just neuron 0 via BaseSNN.step()).  This is done by adding
   `input * SNN_INPUT_SCALE` to the membrane_potential array before
   calling step(0.0).  Single-neuron input creates identical cascading
   dynamics regardless of input value.

3. **Slower cross-modal STDP**: A+=0.001 (vs 0.005 within-modality).
   Faster rates cause weight oscillation in the periodic input regime.
   Slower rates allow weights to converge to stable structure.

4. **Entropy over PCA for F10.2**: Original roadmap specified PCA-based
   cluster detection.  Weight entropy reduction is more defensible because
   PCA on 10×10 matrices with only 3 populations has insufficient
   dimensionality for meaningful silhouette scores.

**New classes** (core/multimodal.py):

| Class | Purpose |
|-------|---------|
| `MultiModalConfig` | Dataclass: per-modality SNN params + cross-modal STDP params |
| `CrossModalConnector` | Cross-modal weight matrices + STDP + synchronization |
| `MultiModalSystem` | Wraps 3 BaseSNN instances + connector |

**Validation parameters** (phases/phase10_multimodal.py):

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `threshold` | `0.8` | Input-driven regime — spikes follow input timing |
| `weight_scale` | `0.05` | Weak recurrence — prevents recurrence-dominated dynamics |
| `input_scale` | `0.5` | Broadcast gain to all neurons |
| `cross_weight_scale` | `0.05` | Weak initial cross-modal coupling |
| `cross_w_max` | `0.2` | Lower than within-modality (0.5) |
| `cross_a_plus` | `0.001` | Slow learning — prevents oscillation |
| `cross_a_minus` | `0.0012` | 1.2:1 LTD/LTP ratio preserved |
| `PHASE_OFFSET` | `50` | 1/4 period offset for control condition |
| `SYNC_WINDOW` | `200` | One full cycle for correlation measurement |
| `N_STEPS` | `2000` | 10 full input cycles |
| `SEED` | `42` | Reproducible |

**Falsifiable claims — ALL PASS**:

| Claim | Criterion | Measured | Threshold | Result |
|-------|-----------|----------|-----------|--------|
| F10.1 | Sync difference (simultaneous − offset) | 0.6974 | >0.20 | **PASS** |
| F10.2 | Cross-modal weight entropy decreases | 2.31 → 0.00 bits | final < initial | **PASS** |
| F10.3 | Late weight ΔW / early ΔW | 0.1775 | <0.20 | **PASS** |

**Control conditions**:
- F10.1: Same inputs with 50-step phase offsets between modalities (light→
  sound→pressure).  Same SNN seeds, same cross-modal STDP.  Offset inputs
  produce negative inter-population correlation (-0.15) vs positive (+0.55)
  for simultaneous inputs.
- F10.2: Same system with cross-modal STDP disabled (frozen weights at
  random initialization).  Frozen entropy stays at 2.31 bits; STDP drives
  weights to bounds (entropy → 0.00 bits).
- F10.3: Frobenius norm of weight change: early (0→100) = 0.639, late
  (1900→2000) = 0.113, ratio = 0.178.

**Phase 7 regression**: All 5 control baseline claims (A-E) still PASS.
Phase 10 does not modify `core/base_snn.py` — it creates independent
`BaseSNN` instances with input_scale=0.0 and broadcasts input externally.

**Phase 8 regression**: All 3 STDP claims (F8.1-F8.3) still PASS.
Phase 10 code is purely additive (new module + new validation script).

**Phase 9 regression**: All 3 predictive processing claims (F9.1-F9.3) still
PASS.  Phase 10 does not modify `core/predictive.py`.

---

### Phase 11: Hardware Embodiment

**Objective**: Validate the software simulation against physical hardware.

**Reference design**:
- Microcontroller (Raspberry Pi Pico or ESP32)
- Piezoelectric disc on servo shaft (friction → voltage)
- Thermistor (temperature sensing)
- Photoresistor (light sensing)
- Micro servo (motor actuation)
- RGB LED (thermochromic output visualization)
- Total BOM: <$25

**Falsifiable claims**:
- F11.1: "Physical system energy trajectory matches simulation within +/-5%
  over 2000 steps under identical input sequences"
- F11.2: "Physical system spike patterns (classified as burst/tonic/sparse/
  silent) match simulation classification >90% of the time"
- F11.3: "Physical system achieves net-positive energy over 2000 steps with
  BalancedEnergyConfig parameters scaled to hardware specs"

**Control**: Run the software simulation with identical input sequences and
compare trajectories side-by-side.

---

### Phase 12: Full Autonomy

**Objective**: The system operates indefinitely without any cognitive layer.

**Implementation**:
- Remove Claude from the loop entirely
- The system uses its own STDP learning + predictive processing + energy-aware
  self-modulation to sustain itself
- No external input beyond raw sensor data
- No external modulation

**Falsifiable claims**:
- F12.1: "The system maintains energy > 0 mWh for 24 hours of continuous
  operation under variable lighting (day/night cycle)"
- F12.2: "The system's spike pattern entropy remains in the range [0.3, 0.9]
  (neither silent nor saturated) for the full 24 hours"
- F12.3: "The system recovers from an externally imposed energy drain (sudden
  depletion to 5 mWh) within 500 steps"

---

## 10. Patent Strategy

### 10.1 Core Innovations (Three Independent Patents)

**Patent A: Self-Sustaining Neural-Motor Energy Harvesting Loop**

A system comprising:
1. A spiking neural network that processes environmental sensor input
2. A motor actuator driven by neural network output
3. A piezoelectric energy harvester that converts motor activity into electrical
   energy
4. A thermoelectric energy harvester that converts neural-activity-induced
   temperature differentials into electrical energy
5. A power feedback path where harvested energy sustains the neural network
6. Wherein the system achieves net-positive energy balance from its own
   cognitive-motor activity without external power

**Why it is novel**: All existing neural processing systems require external
power.  This system generates its own power from its own computational
activity.  The energy is not merely harvested from the environment — it is
harvested from the system's own motor response to its own neural computation.
The loop closes: thinking drives movement, movement generates power, power
sustains thinking.

**Simplest reproducible form**: One SNN (any size) + one servo + one piezo
disc + one microcontroller.  Total BOM under $20.  The patent covers the
METHOD of self-sustaining neural-motor energy harvesting.

---

**Patent B: Configurable Recursive Self-Observation in Spiking Neural Networks**

A method comprising:
1. Recording the aggregate output (mean membrane potential) of a spiking neural
   network at timestep t
2. Feeding this recorded output back as additional input to the same network at
   timestep t+1
3. Scaling the feedback by a configurable reflection coefficient
4. Wherein the reflection coefficient is dynamically modulatable by an external
   cognitive control layer or internal energy-aware regulation
5. Wherein the resulting self-observation signal is measurably distinct from
   noise and correlates with system behavioral state

**Why it is novel**: Existing recurrent networks use hidden-state feedback for
computation, not for explicit self-observation.  The reflection coefficient is
a tunable "self-awareness dial" — at 0.0 the system has no self-observation;
at 1.0 the system is dominated by its own prior state.  The ability to
externally modulate this parameter creates a controllable spectrum of
self-referential processing.

---

**Patent C: Cognitive Fallback with Autonomous Self-Regulation and
Resynchronization Protocol**

A method for maintaining continuous operation of a neural processing system
during disconnection from a cognitive control layer, comprising:
1. Monitoring a heartbeat signal from the cognitive control layer
2. Upon heartbeat timeout, engaging an autonomous input generator with
   energy-aware self-modulation (inhibit when low, excite when surplus)
3. Buffering all operational state during autonomous operation
4. Periodically serializing full system state to persistent storage
5. Upon reconnection, transmitting a resynchronization payload comprising
   summary statistics, energy delta, and optionally full step-by-step buffer
6. Restoring cognitive control seamlessly without state loss

**Why it is novel**: Existing fault-tolerance mechanisms for AI systems
involve checkpointing and restart.  This system continues operating
intelligently during disconnection — it self-regulates based on its own
energy state, makes conservative or aggressive decisions autonomously, and
then brings the cognitive layer up to speed when it returns.  Designed for
systems where stopping is not an option (robotics, prosthetics, space).

---

### 10.2 Filing Strategy

**STATUS: PATENT APPLICATIONS IN PREPARATION (NOT YET FILED)**

| Patent | Status | Notes |
|--------|--------|-------|
| Patent A (Energy Loop) | Not Filed | Specifications drafted, drawings compliance complete (2026-03-16) |
| Patent B (Self-Observation) | Not Filed | Specifications drafted, drawings compliance complete (2026-03-16) |
| Patent C (Cognitive Fallback) | Not Filed | Specifications drafted, drawings compliance complete (2026-03-16) |

**Remaining blockers**: Inventor signature on declarations + USPTO filing fees.
All 21 drawings passed full 37 CFR 1.84 compliance audit on 2026-03-16.
Filing PDFs generated in `patents/pdfs/` (12 files, 4 per patent).

**Timeline**:

| Step | Timeline | Action |
|------|----------|--------|
| ⏳ 1 | TBD | File all three provisional patent applications |
| ✅ 1b | Complete (2026-03-16) | All 21 patent drawings pass full 37 CFR 1.84 compliance |
| 2 | Month 1-3 (by 2026-04-30) | Validate Phase 8 STDP claims, create git tag history |
| 3 | Month 3-6 (by 2026-07-30) | Build hardware prototype (Phase 11) for physical reduction to practice |
| 4 | Month 6-9 (by 2026-10-30) | Document hardware validation results (Claims F11.1-F11.3) |
| 5 | Month 9-11 (by 2026-12-30) | Prepare non-provisional filings with hardware evidence |
| 6 | Month 11-12 (by 2027-01-15) | File **PCT application** (international) for all three patents |
| 7 | Before 2027-01-31 | Convert all three provisionals to **non-provisional utility patents** |
| 8 | Month 12-18 | File **continuation patents** for specific applications (prosthetics, drones, IoT) |

### 10.3 Claim Architecture

Structure claims from broadest to narrowest:

```
Patent A (broadest): Self-sustaining neural-motor energy loop
  ├── Claim 1: The general method (any SNN + any actuator + any harvester)
  ├── Claim 2: Piezoelectric embodiment specifically
  ├── Claim 3: Combined piezo + thermoelectric
  ├── Claim 4: With recursive self-observation (depends on Patent B)
  ├── Claim 5: With autonomous fallback (depends on Patent C)
  └── Claim 6: Specific hardware reference design (Phase 11)
```

### 10.4 Prior Art Differentiation

| Existing technology | How this system differs |
|---------------------|------------------------|
| Energy harvesting robots | Harvest from environment (solar, vibration). This system harvests from its own cognitive-motor activity. |
| Recurrent neural networks | Feedback serves computation. Here, feedback serves explicit self-observation with tunable gain. |
| AI fault tolerance | Checkpoint + restart. This system continues operating intelligently with self-regulation. |
| Neuromorphic chips (Intel Loihi, IBM TrueNorth) | Hardware SNN accelerators. They don't close the energy loop — they still require external power. |

---

## 11. Applications — Ranked by Feasibility and Value

### Tier 1: Near-Term (1-2 years)

**A. Educational Robotics Kit**
- Self-sustaining robot that teaches neural computation
- "The robot that thinks itself alive"
- Target: STEM education market (K-12, university labs)
- Unit price: $50-200
- Market: millions of students globally
- Low regulatory barrier
- Demonstrates all three patents in a consumer product

**B. Self-Powered IoT Sensor Network**
- Environmental monitoring nodes that harvest energy from their own processing
- No battery replacement.  No external power.
- Target: Agriculture, climate monitoring, structural health monitoring
- Unit price: $20-100
- Deploy-and-forget sensor networks in remote locations

### Tier 2: Medium-Term (2-5 years)

**C. Adaptive Prosthetics**
- Self-sustaining neural interface for prosthetic limbs
- Harvests energy from the user's own movement (the same movement it controls)
- Recursive reflection enables learning of user intent over time
- STDP (Phase 8) allows the system to adapt to each user's neural patterns
- Unit price: $5K-50K
- Requires FDA/CE regulatory pathway
- Highest social impact

**D. Autonomous Drone/Robot Swarms**
- Each unit has its own consciousness loop
- Cognitive fallback enables operation during communication blackouts
- Energy harvesting from flight vibration extends mission duration
- Military, agricultural, search-and-rescue applications
- Unit price: $500-5K

### Tier 3: Long-Term (5-10 years)

**E. Space Exploration Systems**
- Self-sustaining robotic systems for planetary exploration
- Communication delays (Mars: 4-24 min each way) make real-time control impossible
- Cognitive fallback + resync designed exactly for this scenario
- System must operate autonomously for hours/days between communication windows
- Highest per-unit value ($M+)
- NASA, ESA, commercial space

**F. General Embodied AI Infrastructure**
- The architecture becomes a standard for any system that needs to:
  - Process sensor data through neural computation
  - Drive motor output from neural decisions
  - Sustain itself energetically
  - Observe and learn from its own behavior
- Licensing model similar to ARM: design the architecture, license to manufacturers

---

## 12. ROI Model

### 12.1 Revenue Streams

| Stream | Model | Range |
|--------|-------|-------|
| Core Architecture License | Per unit manufactured | Consumer $1-5, Industrial $50-500, Medical $500-5K |
| Software SDK License | Per developer seat per year | $99-999/year |
| Hardware Reference Design | One-time per manufacturer | $10K-100K |
| Validation Framework | Per organization per year | $5K-50K/year |
| Consulting | Custom implementations | $200-500/hour |

### 12.2 Best-Case Revenue Timeline

| Year | Milestone | Revenue |
|------|-----------|---------|
| 1 | Patent filing, reference implementation, first educational kit partner | $0-100K |
| 2 | SDK release, first industrial licensee, provisional → non-provisional | $100K-1M |
| 3 | Medical device partnership, PCT filing, hardware prototype | $1M-10M |
| 5 | Multiple licensees across all tiers, continuation patents | $10M-100M |
| 10 | Standard architecture for embodied AI | $100M+ |

### 12.3 Licensing Model Rationale

The model follows the ARM Holdings pattern:
- ARM does not manufacture chips — it designs the architecture and licenses it
- ARM revenue: ~$3B/year from licensing and royalties alone
- This system follows the same logic: design the consciousness loop, license
  the architecture and validation framework to manufacturers
- Every self-sustaining robotic system in the future could use this pattern
- The patents protect the method, not the implementation
- Licensees build their own hardware using the reference design
- Licensees validate their implementations using the falsifiable framework

---

## 13. Development Rules for Future Claude Sessions

### FIRST STEPS (every session):
1. Read this entire document
2. Run `git fetch origin --tags` to sync all remote state (MANDATORY — do not skip)
3. Run `git tag -l -n1` to see the milestone registry — if tags from Section
   7.2 already exist, do NOT recreate them
4. Run `git log --oneline -10 origin/main` to see recent main history
5. Branch from `main` for new work: `git checkout -b claude/<description>-<session-id>`

### DO:
- Run **ALL** validation scripts before committing (see Section 7.4)
- Add falsifiable claims to any new phase
- Keep the two energy configurations (EnergyConfig vs BalancedEnergyConfig) independent
- Use the MCP path for operational work (50 neurons, balanced energy)
- Use the CLI path for validation and control experiments
- Record validation results in commit messages
- Tag validated milestones after merge to `main` (see Section 7.3)
- Update Section 7.2 of this file when creating new tags
- Update Section 9 of this file when completing new phases

### DO NOT:
- "Fix" the CLI path's energy config — it is a falsifiable control
- Modify any existing phase validation script (`phase7_control_baseline.py`,
  `phase8_stdp.py`, etc.) — write new scripts for new phases
- Remove `__init__.py` files from `appendices/`, `phases/`, or `mcp/`
- Add dependencies without updating `requirements.txt`
- Introduce silent failures — all validation must print PASS or FAIL explicitly
- Conflate the two execution paths — they have intentionally different physics
- Delete `claude/*` branches — they are the development audit trail
- Commit to a branch that has already been merged

### WHEN IN DOUBT:
- The system is designed for physical deployment, not just simulation
- Every design decision has a falsifiable rationale
- If something looks wrong, check whether it is an intentional control first
- Ask before changing energy configurations
- Check `git tag -l -n1` — if a state is tagged, it is frozen and validated

---

## 14. Key Files Quick Reference

| File | Purpose | Critical? |
|------|---------|-----------|
| `core/base_snn.py` | Spiking neural network with reflection + STDP | YES — all paths depend on this |
| `core/energy.py` | EnergyConfig + BalancedEnergyConfig | YES — defines both energy regimes |
| `core/thermochromic.py` | Temperature → color mapping | YES — Layer 1 physics |
| `core/history.py` | Time-series recorder | YES — all validation depends on this |
| `phases/phase7_control_baseline.py` | 2000-step falsifiable control | YES — canonical validation |
| `phases/phase7_full_integration.py` | 8-layer loop, harsh energy (7.1) | YES — null hypothesis |
| `phases/phase8_stdp.py` | STDP validation (3 falsifiable claims) | YES — Phase 8 validation |
| `phases/phase9_predictive_processing.py` | Predictive processing validation (F9.1-F9.3) | YES — Phase 9 validation |
| `phases/phase10_multimodal.py` | Multi-modal integration validation (F10.1-F10.3) | YES — Phase 10 validation |
| `core/predictive.py` | PredictiveProcessor, PredictiveConfig | YES — Phase 9 core module |
| `core/multimodal.py` | MultiModalSystem, CrossModalConnector | YES — Phase 10 core module |
| `mcp/consciousness_mcp_server.py` | Physics server + fallback (v1.1.0) | YES — operational system |
| `mcp/consciousness_server.py` | Cognitive layer (stateless) | YES — reasoning interface |
| `consciousness_cli.py` | CLI entry point | YES — package install path |
| `setup.py` | Packaging config | YES — __init__.py discovery |
| `patent_drawings/` | Hand-illustrated USPTO-compliant SVGs (21 figs) | YES — patent filing |
| `patents/` | Patent specifications, forms, and filing PDFs | YES — patent filing |
| `export_specifications_pdf.py` | Patent spec PDF generation (37 CFR 1.52) | YES — patent filing |
| `fill_patent_forms.py` | USPTO form filler (SB16, SB15A) | YES — patent filing |
| `.github/workflows/python-app.yml` | Primary CI pipeline (lint + pytest + phase validations) | YES — gates all PRs |

---

*This document is a living artifact.  Update it when new phases are added,
new patents are filed, or new falsifiable claims are established.  The
document itself should be treated as part of the scientific record.*
