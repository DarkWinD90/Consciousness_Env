"""
Phase 7 — Control Baseline Report Generator

Runs the control-only baseline and emits a clean JSON summary
suitable for review, regression testing, and falsification.
"""

import json
import numpy as np
from phases.phase7_control_baseline import run_baseline


def generate_phase7_report(seed: int = 0):
    history = run_baseline(rng_seed=seed)
    N = len(history["t"])
    W = slice(N // 2, N)

    report = {
        "config": {
            "dt": 0.1,
            "N": N,
            "plant": {"m": 1.0, "c": 0.5, "k": 1.0},
            "controller": {"Kp": 0.3, "Kd": 0.4},
        },
        "boundedness": {
            "theta_min_deg": float(history["theta_deg"].min()),
            "theta_max_deg": float(history["theta_deg"].max()),
            "omega_max_rad": float(np.abs(history["omega"]).max()),
            "energy_min": float(history["E"].min()),
            "energy_max": float(history["E"].max()),
            "temp_min": float(history["T"].min()),
            "temp_max": float(history["T"].max()),
        },
        "robustness": {
            "theta_std_deg": float(np.std(history["theta_deg"][W])),
            "omega_std_rad": float(np.std(history["omega"][W])),
        },
        "gain": {
            "corr_L_theta": float(
                np.corrcoef(history["L"], history["theta_deg"])[0, 1]
            )
        },
        "saturation": {
            "theta_sat_ratio": float(
                np.mean((history["theta_deg"] < 2) | (history["theta_deg"] > 178))
            ),
            "energy_floor_ratio": float(np.mean(history["E"] < 1.0)),
        },
    }

    return report


if __name__ == "__main__":
    report = generate_phase7_report(seed=0)
    print(json.dumps(report, indent=2))
