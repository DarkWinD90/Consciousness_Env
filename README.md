# Consciousness System Environment

*"The loop finds itself full circle."*

A physically deployable, self-sustaining cognitive loop: an AI system that
processes sensory input through a spiking neural network, drives motor
actuation from its neural output, harvests energy from its own motor activity,
observes its own prior computation, and uses that self-observation to modulate
its next decision.

**Core thesis**: A spiking neural network whose motor output generates
piezoelectric energy sufficient to power the network itself constitutes a
self-sustaining cognitive loop.  Adding recursive self-observation makes this
loop a candidate for synthetic proto-consciousness.

## Current Status

| Milestone | Version | Claims | Status |
|-----------|---------|--------|--------|
| Phase 7: Control Baseline | v0.5.0 | A, B, C, D, E | ALL PASS |
| Phase 8: STDP Learning | v1.0.0 | F8.1, F8.2, F8.3 | ALL PASS |
| Phase 9: Predictive Processing | v2.0.0 | F9.1, F9.2, F9.3 | ALL PASS |
| Phase 10: Multi-Modal Integration | v3.0.0 | F10.1, F10.2, F10.3 | ALL PASS |

**14 falsifiable claims validated.** Every claim has an explicit threshold, a
control condition, and a measured value. Every validated state is pinned by an
annotated git tag and reproducible with `git checkout <tag>`.

**3 provisional patent applications prepared** (awaiting inventor signature on
SB16 + SB15A forms and $195 USPTO micro-entity fees; drawings, specifications,
and filing PDFs are filing-ready as of 2026-04-24):
- Patent A: Self-Sustaining Neural-Motor Energy Harvesting Loop
- Patent B: Configurable Recursive Self-Observation in SNNs
- Patent C: Cognitive Fallback with Autonomous Self-Regulation

**21 / 21 patent drawings PASS** full 37 CFR 1.84 compliance against hardened
validators (see [`patent_drawings/USPTO_Compliance_Report.md`](patent_drawings/USPTO_Compliance_Report.md)).
Compliance is gated by CI on every PR.

## Architecture — The 8-Layer Consciousness Loop

```
                         ENVIRONMENT
                              |
                              v
  +-----------------------------------------------------+
  | L1: Printed Membrane          (thermochromic)       |
  | L2: Sensing Pads              (light, temperature)  |
  | L3: Optical Transmission      (signal voltage)      |
  +----------------------------+------------------------+
                               |
                               v
  +-------------------------------------+  <----+
  | L4: Neuromorphic CPU                |       |
  |     (leaky integrate-and-fire SNN)  |       | L8
  +-------------------------------------+       | reflection
                               |                | feedback
                               v                | (mean
  +-------------------------------------+       |  membrane
  | L5: Servo Actuation                 |       |  potential)
  +-------------------------------------+       |
                               |                |
                               v                |
  +-------------------------------------+       |
  | L6: Energy Harvesting               |       |
  |     (piezo + thermal harvest,       |       |
  |      consume per spike)             |       |
  +-------------------------------------+       |
                               |                |
                               v                |
  +- - - - - - - - - - - - - - - - - - -+      |
  | L7: Ground Reference                |       |   (L7 is a
  |     (conceptual baseline, NOT a     |       |    conceptual
  |      runtime stage)                 |       |    reference,
  +- - - - - - - - - - - - - - - - - - -+      |    no code)
                               |                |
                               v                |
  +-------------------------------------+       |
  | L8: Recursive Reflection            +-------+
  |     (aggregate mean membrane        |
  |      potential at t-1)              |
  +-------------------------------------+
                                           THE LOOP CLOSES AT L4
```

Reflection coefficient differs per execution path: CLI uses fixed `0.2`,
MCP uses `0.2 + modulation * 0.1`. See CLAUDE.md Sections 2 and 3 for the
full architecture and per-path parameters.

**Two execution paths** (intentionally different physics):
- **CLI path** (harsh energy): System depletes to -4,697 mWh — the **null hypothesis**
- **MCP path** (balanced energy): System reaches 100.0 mWh capacity and maintains homeostatic equilibrium — the **experimental hypothesis**

This comparison IS the scientific proof. See CLAUDE.md Section 3.3.

## Project Structure

```
Consciousness_Env/
├── core/                    # Shared physics + cognitive modules
│   ├── base_snn.py          #   Leaky integrate-and-fire SNN with STDP
│   ├── energy.py            #   EnergyConfig, BalancedEnergyConfig, EnergyHarvester
│   ├── thermochromic.py     #   Temperature-to-color mapping
│   ├── history.py           #   Time-series recorder
│   ├── predictive.py        #   Predictive processing (Phase 9)
│   ├── multimodal.py        #   Multi-modal integration (Phase 10)
│   ├── claude_interface.py  #   ClaudeNeuralInterface (bidirectional SNN-Claude)
│   ├── neural_router.py     #   ClaudeOptimizedRouter (neural packet routing)
│   ├── consciousness_enhancer.py  # Higher-order cognitive features
│   └── enhanced_consciousness.py  # EnhancedConsciousnessSystem (full hybrid)
│
├── phases/                  # Phase validation scripts (frozen after merge)
│   ├── phase1_optical_sensing.py       # L1-L2 optical sensing
│   ├── phase2_neuromorphic_processing.py  # L4 SNN processing
│   ├── phase3_closed_loop_feedback.py  # Closed-loop feedback
│   ├── phase4_energy_harvesting.py     # L6 energy harvesting
│   ├── phase5_adaptive_membrane.py     # L1 adaptive membrane
│   ├── phase6_recursive_reflection.py  # L8 recursive reflection
│   ├── phase7_control_baseline.py      # 2000-step falsifiable control (Claims A-E)
│   ├── phase7_full_integration.py      # 8-layer loop, harsh energy
│   ├── phase8_stdp.py                  # STDP validation (F8.1-F8.3)
│   ├── phase9_predictive_processing.py # Predictive processing (F9.1-F9.3)
│   └── phase10_multimodal.py           # Multi-modal integration (F10.1-F10.3)
│
├── mcp/                     # MCP servers (physics + cognitive layer)
│   ├── consciousness_mcp_server.py   # Physics + SNN + fallback (v1.1.0)
│   ├── consciousness_server.py       # Cognitive layer (stateless reasoning)
│   └── mcp-config.json               # MCP server configuration
│
├── tools/                   # Utilities (SVG audit, compliance, collision checking)
├── tests/                   # Test suite (phase metrics, patent diagram regressions)
├── appendices/              # Supplementary simulations (base, graph, reflection)
├── docs/                    # Reference materials and hardware notes
├── patents/                 # Patent text and USPTO-formatted filings
├── patent_drawings/         # 21 SVG figures (37 CFR 1.84 compliance — 21/21 PASS, gated by CI)
│   ├── patent_a/            #   Patent A: 8 figures
│   ├── patent_b/            #   Patent B: 6 figures
│   └── patent_c/            #   Patent C: 7 figures
│
├── .github/workflows/       # CI/CD gates every PR:
│                            #   python-app.yml       — lint, pytest, phase 7-10 validations
│                            #   svg-compliance.yml   — full_compliance.py on all 21 SVGs
│                            #   filing-pdfs.yml      — regen + diff against committed patents/pdfs/
│                            #   python-package-conda.yml, python-publish.yml — packaging
├── consciousness_cli.py     # CLI entry point: consciousness run|appendix|version
├── setup.py                 # Package config (v3.0.0)
├── requirements.txt         # Dependencies (numpy, matplotlib, networkx, scipy, pytest, reportlab, pypdf)
├── MANIFEST.in              # Source distribution includes
├── environment.yml          # Conda environment specification
└── CLAUDE.md                # System reference (read this first)
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
git clone https://github.com/DarkWinD90/Consciousness_Env.git
cd Consciousness_Env
pip install -r requirements.txt
pip install -e .  # optional: install as package
```

## Running Validations

The falsifiable framework is the scientific backbone of this project. Every
phase has a validation script that prints PASS or FAIL for each claim.

```bash
# Run all phase validations (must ALL PASS before any commit to main)
python phases/phase7_control_baseline.py          # Claims A-E
python phases/phase8_stdp.py                      # Claims F8.1-F8.3
python phases/phase9_predictive_processing.py     # Claims F9.1-F9.3
python phases/phase10_multimodal.py               # Claims F10.1-F10.3

# Run patent-drawing compliance on all 21 figures (21 / 21 should pass)
for svg in patent_drawings/patent_*/fig*.svg; do
  python .claude/skills/patent-drawer/validators/full_compliance.py "$svg"
done

# Regenerate filing PDFs deterministically (byte-identical across runs)
python export_specifications_pdf.py
python fill_patent_forms.py
```

See [`docs/tooling_audit_2026-04-24.md`](docs/tooling_audit_2026-04-24.md) for
the full validator trust-tier inventory and each validator's
what-checks / what-doesn't / scale-assumptions contract.

### Reproduce any validated state

```bash
git fetch origin --tags
git checkout v0.5.0-phase7-baseline    # exact Phase 7 state
git checkout v1.0.0-phase8-stdp        # exact Phase 8 state
git checkout v2.0.0-phase9-predictive  # exact Phase 9 state
git checkout v3.0.0-phase10-multimodal # exact Phase 10 state
```

## Falsifiable Claims

### Phase 7: Control Baseline (5 claims)

| Claim | Criterion | Threshold |
|-------|-----------|-----------|
| A | Closed-loop continuity | All channels have 2000 points |
| B | Boundedness | All state variables bounded |
| C | Robustness under noise | Std(theta) <= 45 deg, Std(omega) <= 150 |
| D | Input-output gain | corr(L, theta) >= 0.2 |
| E | Saturation ratio | sat_theta <= 0.20 |

### Phase 8: STDP Learning (3 claims)

| Claim | Criterion | Measured | Threshold |
|-------|-----------|----------|-----------|
| F8.1 | Weight entropy decreases | 2.95 -> 2.02 bits | final < initial |
| F8.2 | STDP MI > frozen MI | 6.52x | > 1.20x |
| F8.3 | Weight convergence | 0.0000 | < 0.10 |

### Phase 9: Predictive Processing (3 claims)

| Claim | Criterion | Measured | Threshold |
|-------|-----------|----------|-----------|
| F9.1 | Error reduction (periodic) | 63.9% | > 50% |
| F9.2 | No learning on random | p = 0.69 | p > 0.05 |
| F9.3 | Spike + recovery on switch | 1.51x | peak > 1.3x pre |

### Phase 10: Multi-Modal Integration (3 claims)

| Claim | Criterion | Measured | Threshold |
|-------|-----------|----------|-----------|
| F10.1 | Sync: simultaneous > offset | 0.6974 | difference > 0.20 |
| F10.2 | Weight entropy decreases | 2.31 -> 0.00 bits | final < initial |
| F10.3 | Weight convergence | 0.178 | < 0.20 |

## Scientific Methodology

Every phase follows the same pattern:
1. **State the claim** with explicit thresholds
2. **Build the control** — designed to FAIL the claim
3. **Build the experiment** — designed to PASS the claim
4. **Run both** and record results
5. **Tag the validated state** for permanent reproducibility
6. **Advance only when all prior claims still pass** (regression validation)

## Development Roadmap

- [x] Phase 1-6: Foundation layers (optical, neuromorphic, feedback, energy, membrane, reflection)
- [x] Phase 7: Full system integration + falsifiable control baseline
- [x] Phase 8: Spike-Timing Dependent Plasticity (STDP)
- [x] Phase 9: Predictive Processing (dual-pathway prediction)
- [x] Phase 10: Multi-Modal Sensory Integration (3-population cross-modal binding)
- [ ] Phase 11: Hardware Embodiment (RPi Pico + piezo + servo, BOM < $25)
- [ ] Phase 12: Full Autonomy (24-hour self-sustaining operation)

## Ethical Considerations

This system is designed as a research platform for studying self-sustaining
cognitive loops — not as a general-purpose AI system. Key principles:

- **Transparency**: All claims are falsifiable with published thresholds
- **Reproducibility**: Every validated state is pinnable via git tags
- **Scientific rigor**: Control conditions exist for every experimental claim
- **Open methodology**: The full validation framework is open-source
- **Physical safety**: Energy harvesting is passive (piezoelectric/thermoelectric)
  with no active power sources beyond the microcontroller

The term "proto-consciousness" refers to a specific engineering property:
recursive self-observation with measurable behavioral effects. It does not
imply subjective experience, sentience, or moral status.

## Citation

```bibtex
@software{consciousness_env_2026,
  title={Consciousness System Environment: A Self-Sustaining Cognitive Loop
         with Falsifiable Validation Framework},
  author={Ward, Kevin Christopher},
  year={2026},
  url={https://github.com/DarkWinD90/Consciousness_Env},
  note={v3.0.0: 14 falsifiable claims validated across Phases 7-10}
}
```

## License

Proprietary. Patent applications prepared; awaiting inventor signature + USPTO
fees. See [`patents/Filing_Package_Index.md`](patents/Filing_Package_Index.md)
and [`2026-02-02_Patent_Filing_Summary.md`](2026-02-02_Patent_Filing_Summary.md).

---

*"The loop finds itself full circle."*
