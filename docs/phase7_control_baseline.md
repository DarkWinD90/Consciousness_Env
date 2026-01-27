# Phase 7 — Control-First Integration (Complete Adjustments + Falsifiable Proofs)

This document defines the **Phase 7 control-baseline** precisely enough to implement and to falsify.
It is designed to replace any "interpretive" wording with **testable claims, measurable metrics, and pass/fail criteria**.

---

## 0) Phase 7 Scope (Locked)

### Phase 7 **is**
A **closed-loop control integration checkpoint**: integrate sensing models, a controller, a plant model, energy accounting, and reference/noise into one loop, then test **stability + observability** under a canonical input.

### Phase 7 **is not**
Phase 7 does **not** demonstrate:
- consciousness / awareness / agency
- hardware-accurate grounding behavior
- net-positive energy generation / physical self-powering
- biological emergence

All components are **modeled** (abstract), and Phase 7 is the **baseline reference frame** for later empirical validation.

---

## 1) Locked Control Decisions (From your answers)

### (1) Plant model
**Second-order plant** (inertia + damping + stiffness), i.e. mass-spring-damper.

### (2) Primary stability metric
**Boundedness** is the primary metric (hard pass/fail).

### (3) Secondary robustness metric
**Variance under noise** is the companion metric (robustness under stochastic perturbations).

### (4) Canonical input profile
**Slow day/night sinusoid**: period = **200 steps** (discrete-time).

### (5) Internal state definition
**State feedback (observable vector)**: controller state uses a logged vector of key variables
(e.g., temperature proxy, energy, joint angle, joint velocity).

---

## 2) System Definition (Control Baseline)

### 2.1 Discrete time
Let time be indexed by steps: `t = 0, 1, 2, ...` with fixed `Δt` (choose `Δt = 1` in sim for simplicity unless you prefer a physical value).

### 2.2 Canonical input: day/night sinusoid + noise
Define the canonical environmental light input `L(t)` as:

- Base sinusoid (period 200 steps):
  - `L_base(t) = L0 + A * sin(2π t / 200)`
- Additive noise:
  - `ε(t) ~ Normal(0, σ_L)`
- Clamp to physical minimum:
  - `L(t) = max(0, L_base(t) + ε(t))`

**Default suggestion (safe):**
- `L0 = 500`, `A = 300`, `σ_L = 50`

> These are not "true," they're chosen to create a repeatable stimulus for control testing.

### 2.3 Observable state vector
Recommended state vector (all logged):
- `θ(t)` : joint angle (deg or rad)
- `ω(t)` : joint angular velocity
- `E(t)` : energy storage (modeled)
- `T(t)` : temperature proxy (modeled)
- Optional (if kept): controller state summary `x_c(t)`

Define:
- `x(t) = [θ(t), ω(t), E(t), T(t)]^T`

### 2.4 Second-order plant (mass-spring-damper)
Continuous form:
- `m θ̈ + c θ̇ + k θ = u`

Discrete-time update (simple Euler is fine for baseline):
- `ω(t+1) = ω(t) + Δt * (u(t) - c ω(t) - k θ(t)) / m`
- `θ(t+1) = θ(t) + Δt * ω(t+1)`

**Default baseline parameters (your recommendation):**
- `m = 1.0`, `c = 0.5`, `k = 1.0`, `Δt = 1.0`

### 2.5 Controller (state feedback, simple but falsifiable)
We want the controller to be **explicit, interpretable, and debuggable**.
A minimal baseline controller:

1) Map light to a reference angle:
- `θ_ref(t) = θ_mid + θ_amp * s(L(t))`
Where `s(·)` is a normalized mapping (e.g., clamp to [0,1]).

2) Use a PD controller on the plant:
- `u(t) = Kp * (θ_ref(t) - θ(t)) - Kd * ω(t)`

**Default baseline gains (safe starting point):**
- `Kp = 1.5`, `Kd = 0.6`
- `θ_mid = 90°`, `θ_amp = 60°`
- Clamp `θ_ref` to `[0°, 180°]` if you keep servo semantics.

> This replaces "mystical" processing with a control baseline.
> You can still keep the SNN as an **optional module**, but Phase 7 baseline must remain runnable and interpretable without it.

### 2.6 Energy accounting (modeled, boundedness-focused)
Energy update:
- `E(t+1) = E(t) + α*(H(t) - C(t))`

Where:
- `H(t)` is modeled harvest (optional) and **must not be used to claim self-powering**
- `C(t)` is modeled consumption (base + motion-related)

Recommended minimal model:
- `C(t) = C0 + C_move * |u(t)|`
- `H(t) = H0 + H_temp * |T(t) - T_amb|`  (optional)

**Default:**
- `C0 = 0.3`, `C_move = 0.02`
- `α = 0.1`
- `H0 = 0.0` initially (keep honest); enable harvest later once control is stable.

Define **hard bounds**:
- `E_min`, `E_max` (e.g., 0 to 100)

Then clamp:
- `E(t+1) = clip(E(t+1), E_min, E_max)`

### 2.7 Temperature proxy (optional but consistent)
A simple thermodynamic proxy is fine:
- `T(t+1) = T(t) + β * L(t) - γ*(T(t) - T_amb)`
Defaults:
- `β = 1/500`, `γ = 0.05`, `T_amb = 20°C`

---

## 3) Falsifiable Claims ("Proof Obligations")

Phase 7 is **successful** only if the following claims are met *under the canonical input profile*.

### Claim A — Closed-loop continuity (falsifiable)
**Statement:** The integrated loop runs for `N` steps without external intervention (no manual resets, no NaNs, no crashes).

**Proof:** A run log exists with exactly `N` samples for every logged variable.
- Required: `len(history[var]) == N` for all variables.

**Pass/Fail:** PASS if all channels have `N` points.

### Claim B — Boundedness of state (primary stability; falsifiable)
**Statement:** All primary state variables remain within predefined bounds for the full run.

Define bounds (example):
- `θ ∈ [0°, 180°]`
- `|ω| ≤ ω_max` (choose e.g. `ω_max = 300°/step` for baseline)
- `E ∈ [E_min, E_max]`
- `T ∈ [T_min, T_max]` (choose e.g. `[-20°C, 80°C]`)

**Proof:** Compute:
- `max_t θ(t)`, `min_t θ(t)`, etc.
- Confirm all within bounds.

**Pass/Fail:** FAIL if any variable crosses bounds at any time.
This is a hard falsifier.

### Claim C — Robustness under noise (variance criterion; falsifiable)
**Statement:** Under canonical input + noise (`σ_L`), output variability remains below a chosen threshold.

Define a steady window `W` (e.g., last 50% of the run) and compute:
- `Var_W(θ)` or `Std_W(θ)`
- `Var_W(ω)`

**Suggested baseline threshold (tune later):**
- `Std_W(θ) ≤ 25°`  (example)
- `Std_W(ω) ≤ 150°/step`

**Proof:** Report computed standard deviations and compare to thresholds.

**Pass/Fail:** FAIL if variance exceeds threshold.

### Claim D — Input-Output gain exists (nontriviality; falsifiable)
**Statement:** The system is responsive to environmental input; outputs are not constant or decoupled.

Compute correlation over the run:
- `ρ = corr(L(t), θ_ref(t))` should be high by construction
- `corr(L(t), θ(t))` should be **non-zero** and positive

**Baseline criterion:**
- `corr(L, θ) ≥ 0.2` (example; calibrate)

**Proof:** Report the correlation coefficient.

**Pass/Fail:** FAIL if correlation is near zero (system not responding).

### Claim E — No pathological saturation (falsifiable)
**Statement:** The system does not spend most of the run pegged at bounds (which would indicate trivial clipping rather than control).

Define saturation ratio:
- `sat_θ = (# timesteps where θ is within δ of 0 or 180) / N`
Pick δ (e.g., 2°).

**Baseline criterion:**
- `sat_θ ≤ 0.20`

**Pass/Fail:** FAIL if the joint is saturated >20% of the time.

---

## 4) Phase 7 Validation Report (What you should output each run)

At the end of each run, print or save a **Phase 7 report** containing:

- Run settings: `N`, `Δt`, `L0`, `A`, `σ_L`
- Plant: `m`, `c`, `k`
- Controller gains: `Kp`, `Kd`
- Energy bounds: `E_min`, `E_max`
- Metrics:
  - Boundedness checks (min/max for each state)
  - Noise robustness (`Std_W(θ)`, `Std_W(ω)`)
  - Correlation (`corr(L, θ)`)
  - Saturation ratio (`sat_θ`)
- Overall: PASS/FAIL and which claim failed

This is your falsifiable "receipt."

---

## 5) Repo Alignment Checklist (Concrete implementation steps)

### 5.1 Language updates (README / docs)
Update Phase 7 language to explicitly state:
- control-baseline purpose
- second-order plant
- boundedness + variance metrics
- non-claims (no consciousness, no hardware grounding claims)

### 5.2 Code updates (Phase 7 script)
Implement, in order:

1) **Canonical input function** `L(t)` with period=200 and Gaussian noise
2) **Second-order plant** state `(θ, ω)` with discrete update
3) **State feedback controller** (PD baseline)
4) **Energy accounting** with hard bounds and explicit clamp
5) Logging of all variables (including `θ_ref`, `u`, and noise parameters)
6) Validation report printing Claim A-E with PASS/FAIL

### 5.3 Optional: keep SNN without contaminating baseline
If you keep the neuromorphic block, ensure:
- Phase 7 baseline can run **without it**
- SNN becomes a pluggable controller option
- Metrics are identical regardless of controller choice

This prevents interpretive creep and keeps Phase 7 falsifiable.

---

## 6) Minimal File/Folder Additions

- `phases/phase7_control_baseline.py`  (the authoritative baseline)
- `docs/phase7_control_baseline.md`    (this document)
- `tests/test_phase7_metrics.py`       (unit tests for metrics/validation logic)

---

## 7) Suggested Default Run Configuration (Start Here)
- Steps: `N = 2000` (10 full day/night cycles if period=200)
- Noise: `σ_L = 50`
- Plant: `m=1`, `c=0.5`, `k=1`
- Controller: `Kp=1.5`, `Kd=0.6`
- Energy: `E_min=0`, `E_max=100`, `E0=50`
- Temperature: `T_amb=20`, `β=1/500`, `γ=0.05`

---

## 8) What Phase 7 "Proves" (and what it does not)

### It can prove (within the simulation):
- the integrated loop is stable (bounded) under a canonical forcing input
- the system remains observable and produces reproducible metrics
- the system is robust to defined noise levels

### It cannot prove:
- physical grounding effects
- hardware energy autonomy
- consciousness or emergence

Those require later empirical phases.

---

## 9) Next Step After Phase 7 Passes
Once Phase 7 passes under the above criteria, the next subsystem to validate empirically should be chosen by answering:

> "Which Phase 7 assumption is most likely to fail in hardware first?"

In most cyber-physical systems, that is: **ground reference + noise + actuation coupling**.
That naturally leads into the **grounded leg** as an experimental instrument.
