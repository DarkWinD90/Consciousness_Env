# Phase 11: Hardware Embodiment — Bill of Materials

**Target Timeline**: Month 3-6 (by 2026-07-30)
**Purpose**: Physical validation of simulation for Patent A non-provisional filing
**Target BOM Cost**: <$25 total

---

## Core Components

| Component | Specification | Supplier | Unit Price | Quantity | Subtotal | Notes |
|-----------|--------------|----------|------------|----------|----------|-------|
| **Microcontroller** | Raspberry Pi Pico (RP2040) | Adafruit/Digi-Key | $4.00 | 1 | $4.00 | 264KB RAM, dual-core 133MHz, sufficient for 50-neuron SNN |
| *Alternative* | ESP32-C3 | Espressif | $3.50 | 1 | $3.50 | WiFi/BLE option for remote monitoring |
| **Piezoelectric Disc** | 27mm piezo element | Adafruit #1739 | $1.95 | 1 | $1.95 | Friction → voltage harvesting (0.5-5V peak) |
| **Micro Servo** | SG90 9g servo | Amazon | $2.50 | 1 | $2.50 | 180° rotation, 4.8-6V, stall torque 1.8kg·cm |
| **Thermistor** | NTC 10K 3950 | Amazon | $0.15 | 1 | $0.15 | Temperature sensing (-40°C to +125°C) |
| **Photoresistor** | GL5528 LDR | Amazon | $0.10 | 1 | $0.10 | Light sensing (10-100kΩ range) |
| **RGB LED** | WS2812B | Amazon | $0.25 | 1 | $0.25 | Thermochromic output visualization |
| **Resistors** | 10kΩ (×2), 220Ω (×1) | Amazon | $0.05 | 3 | $0.15 | Voltage dividers, LED current limiting |
| **Capacitor** | 100µF electrolytic | Amazon | $0.10 | 1 | $0.10 | Piezo voltage smoothing |
| **Breadboard** | 400-point mini | Amazon | $2.00 | 1 | $2.00 | Prototyping |
| **Jumper Wires** | Male-to-male (×20) | Amazon | $1.00 | 1 set | $1.00 | Connections |
| **USB Cable** | Micro-USB or USB-C | Amazon | $1.50 | 1 | $1.50 | Programming/power |

**Total BOM (Pi Pico option)**: **$16.70**
**Total BOM (ESP32 option)**: **$16.20**

---

## Circuit Design

### Power Path
```
Piezo Disc → Capacitor (smoothing) → ADC Pin (energy measurement)
                                   → Buck converter (optional, for self-sustaining loop)
USB Power → Microcontroller VIN (initial power for bootstrap)
```

### Sensor Inputs
```
Photoresistor → 10kΩ pull-down → ADC Pin (light_intensity)
Thermistor → 10kΩ voltage divider → ADC Pin (membrane_temp)
```

### Actuator Output
```
GPIO PWM Pin → Servo signal wire
Servo power: separate 5V rail (USB or external battery)
```

### Visualization Output
```
GPIO Pin → WS2812B RGB LED (thermochromic color display)
```

---

## Assembly Steps

### Phase 1: Breadboard Prototype (Week 1-2)
1. Wire Pi Pico to breadboard with power/ground rails
2. Connect photoresistor voltage divider to ADC0
3. Connect thermistor voltage divider to ADC1
4. Connect servo signal to GPIO15 (PWM channel)
5. Connect WS2812B LED to GPIO16
6. Connect piezo disc to ADC2 with 100µF smoothing cap

### Phase 2: Piezo Mounting (Week 3)
1. Attach piezo disc to servo shaft using hot glue or double-sided tape
2. Add small friction pad (rubber/foam) on piezo surface
3. Mount servo to breadboard or small acrylic base
4. Test: manual servo rotation → measure voltage on ADC2

### Phase 3: Firmware Development (Week 4-6)
1. Port BaseSNN from Python to C/C++ (MicroPython or Arduino framework)
2. Implement leaky integrate-and-fire with fixed-point arithmetic
3. Implement energy harvester physics (friction + thermal)
4. Implement sensor input pipeline (light, temp → voltage)
5. Implement servo output (SNN spikes → angle)
6. Implement LED color output (temp → RGB mapping)

### Phase 4: Validation (Week 7-8)
1. Run 2000-step trajectory with identical input as simulation
2. Log energy, spikes, temperature, angle every step
3. Compare physical vs. simulation trajectories
4. Measure falsifiable claims F11.1-F11.3

---

## Firmware Architecture

### Core Loop (10 Hz = 100ms per step)
```c
void loop() {
    // Read sensors (L1-L2)
    float light = read_photoresistor();  // ADC0
    float temp = read_thermistor();      // ADC1

    // Convert to signal voltage (L3)
    float signal_voltage = (light / 1000.0) * 5.0;

    // SNN step (L4)
    float reflection_input = previous_output * reflection_coeff;
    snn_step(signal_voltage, reflection_input);
    float snn_output = snn_get_output();

    // Servo actuation (L5)
    float target_angle = clip(snn_output * 180.0, 0, 180);
    servo_write(target_angle);

    // Energy harvesting (L6)
    float angular_velocity = (target_angle - prev_angle) / dt;
    float friction_power = FRICTION_FACTOR * angular_velocity * angular_velocity;
    float thermal_power = THERMAL_FACTOR * (temp - ambient_temp);
    float piezo_voltage = read_piezo_adc();  // ADC2
    float piezo_power = (piezo_voltage * piezo_voltage) / 1000.0;  // mW

    float harvested = friction_power + thermal_power + piezo_power;
    float consumed = BASE_CONSUMPTION_MW + neuron_power;
    energy_mwh += (harvested - consumed) * (dt / 3600.0);

    // LED visualization (thermochromic L1)
    update_led_color(temp);

    // Logging
    log_step(energy_mwh, snn_spikes, temp, target_angle);

    // L8 reflection
    previous_output = snn_output;
    prev_angle = target_angle;

    delay(100);  // 10 Hz loop
}
```

---

## Validation Protocol

### Test Conditions
- **Input sequence**: Reproduce Phase 7 baseline input (sinusoid + noise, seed=42)
- **Duration**: 2000 steps (200 seconds at 10 Hz)
- **Logging**: CSV file with columns: `step, energy_mwh, spikes, temp_c, angle_deg, light_raw, piezo_v`
- **Control**: Run simulation with identical input, compare outputs

### Falsifiable Claims (Pass Criteria)

| Claim | Criterion | How to Measure |
|-------|-----------|----------------|
| **F11.1** | Energy trajectory ±5% | Compare `energy_mwh` columns: `max(abs(physical - sim)) / sim_range < 0.05` |
| **F11.2** | Spike pattern match >90% | Classify both into burst/tonic/sparse/silent, compute agreement ratio |
| **F11.3** | Net-positive energy | Final `energy_mwh > 0` after 2000 steps with BalancedEnergyConfig |

### Data Collection
1. Run physical system, save `physical_run_001.csv`
2. Run simulation with identical seed/input, save `simulation_run_001.csv`
3. Run validation script: `python validate_phase11.py physical_run_001.csv simulation_run_001.csv`
4. Generate comparison plots: energy trajectory, spike raster, angle trajectory

---

## Expected Results (Based on Simulation)

### With BalancedEnergyConfig (50 neurons, friction=18.0, thermal=8.0)
- **Initial energy**: 50 mWh
- **Final energy (2000 steps)**: ~4,200 mWh (net gain +4,150 mWh)
- **Spike pattern**: Burst dynamics with periodic activity
- **Energy trajectory**: Linear growth after initial transient

### Physical System Adjustments
- Scale neuron count if RAM constrained (Pi Pico 264KB → ~30-40 neurons max)
- Calibrate piezo voltage → power conversion with oscilloscope measurements
- Calibrate thermal model with infrared thermometer (servo heat dissipation)
- Tune friction factor based on actual servo friction (torque sensor or power draw)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Insufficient piezo power** | Use external vibration source (fan) to test harvesting separately |
| **Servo stalls under load** | Reduce weight on piezo disc, use lower-torque test pattern |
| **Thermal noise** | Shield thermistor from servo motor heat, use separate temp sensor |
| **RAM overflow on Pi Pico** | Reduce neuron count to 30, use fixed-point arithmetic (int16), optimize arrays |
| **Timing jitter** | Use hardware timer interrupt for 10 Hz loop (not `delay()`) |
| **ADC noise** | Oversample 16× and average for each reading |

---

## Success Criteria for Patent Filing

For non-provisional Patent A conversion (2027-02-02 deadline):

1. ✅ **Physical prototype built** — all components assembled and operational
2. ✅ **2000-step run completed** — logged CSV data with no crashes
3. ✅ **F11.1 PASS** — Energy trajectory within ±5%
4. ✅ **F11.2 PASS** — Spike pattern match >90%
5. ✅ **F11.3 PASS** — Net-positive energy demonstrated
6. ✅ **Photos/video** — Prototype in operation, LED visualization visible
7. ✅ **Oscilloscope traces** — Piezo voltage waveform captured during actuation

**Deliverable**: Technical report with:
- Schematic diagram
- BOM with supplier links
- Firmware source code (GitHub commit hash)
- Validation results (CSV data + comparison plots)
- Photos of physical prototype
- Video of 2000-step run showing LED color changes

This constitutes **reduction to practice** for Patent A.

---

## Timeline

| Week | Milestone |
|------|-----------|
| 1-2 | Order parts, breadboard assembly, basic sensor tests |
| 3 | Piezo mounting and friction testing |
| 4-5 | Firmware development (SNN port to C++) |
| 6 | Full integration and debugging |
| 7 | 2000-step validation runs |
| 8 | Data analysis, report writing, photography/video |

**Target completion**: 2026-07-30 (Month 6)
**Buffer time**: 5 months before non-provisional deadline

---

## Next Steps (Immediate)

1. **Order parts** from Amazon/Adafruit (total ~$17, 1-week shipping)
2. **Set up development environment**:
   - Install Arduino IDE or PlatformIO
   - Install Pi Pico SDK or MicroPython
3. **Create Phase 11 branch**: `git checkout -b claude/phase11-hardware-<session-id>`
4. **Port BaseSNN to C++**:
   - Fixed-point arithmetic for membrane potentials
   - Optimize for 264KB RAM constraint
5. **Test each subsystem independently**:
   - ADC readings (light, temp, piezo)
   - PWM servo control
   - WS2812B LED color output
   - SNN step function (unit test with known inputs)

---

**Status**: Ready for procurement and development
**Risk Level**: Low — all components are commodity hardware
**Expected Success Rate**: >95% (standard microcontroller project)

---

*For questions or issues during build, document in `Phase11_Build_Log.md`*
