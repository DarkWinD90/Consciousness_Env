# Phase 11: Hardware Embodiment Specification

## Overview

This document defines the hardware architecture for the physical instantiation
of the Consciousness Loop. The design prioritizes:

- **Serial bus servos** over PWM (scalable to 16+ actuators)
- **Banked power distribution** with optional per-bank current sensing
- **Energy harvesting** from piezo and thermal sources
- **LiFePO4 battery chemistry** for safety and longevity

---

## 1. Power Architecture

### Battery
| Parameter | Value | Notes |
|-----------|-------|-------|
| Chemistry | LiFePO4 | Long cycle life, safer, flat discharge curve |
| Nominal | 3.2V/cell | 2S = 6.4V nominal |
| Capacity | TBD | Sized for 16+ servos at full load |

### Power Rails
| Rail | Voltage | Source | Loads |
|------|---------|--------|-------|
| VBAT_SERVO | 6V | Battery + regulator | Servo banks A/B/C/D |
| 5V | 5V | Buck/LDO from battery | WS2812B LED |
| 3V3 | 3.3V | Pico onboard regulator | Logic, sensors, ADC ref |

---

## 2. Controller (U1: RP2040 / Raspberry Pi Pico)

### Pin Assignments
| Signal | GPIO | Function | Notes |
|--------|------|----------|-------|
| SERVO_BUS_TX | GP0 | UART0 TX | Half-duplex to bus buffer |
| SERVO_BUS_DIR | GP1 | Digital out | Direction control for buffer |
| I2C0_SDA | GP4 | I2C data | Current sensors (INA219) |
| I2C0_SCL | GP5 | I2C clock | Current sensors (INA219) |
| LED_DIN | GP15 | Digital out | WS2812B data |
| ADC_PZ | GP26 | ADC0 | Piezo voltage sense |
| ADC_LDR | GP28 | ADC2 | LDR light intensity |

### Reserved/Available
| GPIO | Status | Notes |
|------|--------|-------|
| GP2-GP3 | Reserved | UART1 (debug/expansion) |
| GP6-GP14 | Available | Future expansion |
| GP16-GP22 | Available | Future expansion |
| GP27 | ADC1 | Thermal sense (optional) |

---

## 3. Servo Bus Architecture

### Removed (from prototype design)
- ~~SERVO_PWM~~ — no longer using PWM per servo
- ~~PCA9685 PWM expander~~ — not needed with serial bus

### Bus Interface Circuit
```
                    3V3
                     │
              ┌──────┴──────┐
              │   U2: 74LVC1G125   │
GP0 (TX) ────▶│ A        Y │────┬────▶ SERVO_BUS
              │             │    │
GP1 (DIR) ───▶│ OE         │    ├── R_TERM (120Ω) ── GND
              └─────────────┘    │
                                 └── D_PROT (TVS)
```

| Component | Value | Purpose |
|-----------|-------|---------|
| U2 | 74LVC1G125 | Tri-state buffer, 3.3V→5V level shift |
| R_TERM | 120Ω | Line termination (optional, for long runs) |
| D_PROT | TVS (SMBJ5.0A) | ESD protection on bus |

### Communication Protocol
| Parameter | Value |
|-----------|-------|
| Protocol | Half-duplex UART (Feetech SCS/STS compatible) |
| Baud rate | 1 Mbps (default) |
| Voltage | 5V TTL |
| Addressing | 1-253 (per Feetech protocol) |

---

## 4. Servo Power Banks

### Bank Configuration
| Bank | Servos | Connector | Current Sense |
|------|--------|-----------|---------------|
| BANK_A | 1-4 | 4-pin header | INA219 @ 0x40 (opt) |
| BANK_B | 5-8 | 4-pin header | INA219 @ 0x41 (opt) |
| BANK_C | 9-12 | 4-pin header | INA219 @ 0x44 (opt) |
| BANK_D | 13-16 | 4-pin header | INA219 @ 0x45 (opt) |

### Connector Pinout (per bank)
| Pin | Signal |
|-----|--------|
| 1 | GND |
| 2 | VBAT_SERVO (6V) |
| 3 | VBAT_SERVO (6V) |
| 4 | SERVO_BUS |

### Per-Bank Current Sensing (Optional)
```
VBAT_SERVO ──┬── R_SHUNT (0.01Ω 1%) ──┬── BANK_x_6V
             │                         │
             └── INA219 VIN+    VIN- ──┘
                    │
              SDA/SCL to Pico (I2C0)
```

| Parameter | Value |
|-----------|-------|
| Shunt resistor | 0.01Ω ±1% |
| Max current | 3.2A per bank (INA219 limit) |
| I2C addresses | 0x40, 0x41, 0x44, 0x45 |

**Benefits:**
- Energy-aware control: current draw feeds back to SNN
- Stall detection: identify overloaded servos
- Patent A validation: correlate motor activity with piezo harvest

---

## 5. Sensing

### Piezo Disc (PZ1)
| Parameter | Value |
|-----------|-------|
| Type | 27mm piezoelectric disc |
| Function | Dual-use: energy harvest + vibration sense |
| ADC input | GP26 (ADC0) via C4 filter |

### Light Sensor (LDR1)
| Parameter | Value |
|-----------|-------|
| Type | GL5528 photoresistor |
| Divider | R3 = 10kΩ to GND |
| ADC input | GP28 (ADC2) |
| Voltage | 0-3.3V (dark=high, bright=low) |

### Temperature Sensor (TH1)
| Parameter | Value |
|-----------|-------|
| Type | NTC thermistor 10kΩ |
| Beta | 3950K |
| Divider | 10kΩ to 3V3 |
| ADC input | GP27 (ADC1) — optional |

---

## 6. Energy Harvesting

### Piezo Harvesting Path
```
PZ1 ──▶ L1 (ferrite) ──▶ BR1 (Schottky bridge) ──▶ C1 (100µF) ──┐
                                                                 │
                                                          D9 (OR)├──▶ C3 (supercap)
                                                                 │
TH1 ──▶ TEG (optional) ──▶ BR2 (Schottky bridge) ──▶ C2 (100µF)──┘
                                                          D10 (OR)
```

### Components
| Ref | Component | Value | Notes |
|-----|-----------|-------|-------|
| L1 | Ferrite inductor | TBD | Tuned to piezo resonance |
| BR1 | Schottky bridge | MB10S or 4× BAT54 | Piezo rectification |
| BR2 | Schottky bridge | MB10S or 4× BAT54 | Thermal rectification (opt) |
| C1, C2 | Smoothing cap | 100µF 16V | Post-rectification |
| D9, D10 | OR-ing diodes | BAT54 Schottky | Combine harvest sources |
| C3 | Storage cap | Supercap TBD | Energy reservoir |
| C4 | ADC filter | 0.1µF | On ADC_PZ input |

---

## 7. LED Output

### WS2812B Interface
```
GP15 ──▶ R4 (330Ω) ──▶ LED1 (WS2812B) DIN
                              │
                         VDD ─┴─ 5V rail
```

| Component | Value | Notes |
|-----------|-------|-------|
| R4 | 330Ω | Series resistor on data line |
| LED1 | WS2812B | Addressable RGB LED |
| Level shift | Optional | 74LVC1G17 for 3.3V→5V (recommended) |

---

## 8. Test Points

| TP | Net | Purpose |
|----|-----|---------|
| TP1 | GND | Ground reference |
| TP2 | 3V3 | Logic rail verification |
| TP3 | VBAT_SERVO | 6V servo rail (pre-bank) |
| TP4 | SERVO_BUS | Serial bus probe point |
| TP5 | ENERGY_STORE | Harvested energy (C3 voltage) |

---

## 9. Connectors

| Connector | Pins | Signal |
|-----------|------|--------|
| J_SERVO_A | 4 | GND / 6V / 6V / BUS |
| J_SERVO_B | 4 | GND / 6V / 6V / BUS |
| J_SERVO_C | 4 | GND / 6V / 6V / BUS |
| J_SERVO_D | 4 | GND / 6V / 6V / BUS |
| J_LED | 3 | GND / 5V / DIN |
| J_PIEZO | 2 | PZ+ / PZ- |
| J_THERMAL | 2 | TEG+ / TEG- |
| J_DEBUG | 4 | GND / 3V3 / TX / RX (UART1) |

---

## 10. Servo Recommendations

### Recommended Models (Serial Bus)
| Model | Torque | Voltage | Protocol | Price | Use Case |
|-------|--------|---------|----------|-------|----------|
| Feetech SCS15 | 15 kg·cm | 6-7.4V | TTL serial | ~$20 | General joints |
| Feetech STS3215 | 15 kg·cm | 6-7.4V | TTL serial | ~$25 | With position feedback |
| Feetech SCS225 | 25 kg·cm | 6-7.4V | TTL serial | ~$35 | Load-bearing (hips, shoulders) |

### Hybrid Configuration (16 servos)
| Joint Type | Model | Qty | Notes |
|------------|-------|-----|-------|
| High-load | SCS225 (25kg) | 4-6 | Hips, shoulders, spine |
| Medium-load | STS3215 (15kg) | 6-8 | Elbows, knees, wrists |
| Low-load | SCS15 (15kg) | 4-6 | Fingers, head pan/tilt |

**Why serial bus servos?**
- Position/velocity/load feedback (closes the SNN loop)
- Single data wire daisy-chain (16 servos on 1 UART)
- Addressable IDs (no GPIO multiplexing)
- 6V compatible (matches power architecture)

---

## 11. Bill of Materials (Preliminary)

| Qty | Ref | Description | Est. Cost |
|-----|-----|-------------|-----------|
| 1 | U1 | Raspberry Pi Pico | $4 |
| 1 | U2 | 74LVC1G125 tri-state buffer | $0.50 |
| 4 | INA219 | Current sensor module (optional) | $8 |
| 1 | PZ1 | 27mm piezo disc | $2 |
| 1 | LDR1 | GL5528 photoresistor | $0.50 |
| 1 | TH1 | NTC 10k thermistor | $1 |
| 1 | LED1 | WS2812B module | $1 |
| 16 | - | Serial bus servos (mixed) | $320-400 |
| 1 | - | LiFePO4 2S battery pack | $25-50 |
| - | - | Passives, connectors, PCB | $20-30 |
| | | **Total (estimated)** | **$400-500** |

---

## 12. Firmware Interface Mapping

The hardware maps to the MCP server's consciousness system as follows:

| Hardware | MCP Tool | SNN Input/Output |
|----------|----------|------------------|
| ADC_PZ (piezo) | `step_simulation.external_input` | Layer 2 sensor input |
| ADC_LDR (light) | `step_simulation.external_input` | Layer 1 membrane |
| Servo position feedback | `get_neural_state` | Layer 8 reflection |
| Servo torque/current | `get_system_status.energy_status` | Layer 6 energy |
| Per-bank current | Energy harvester correlation | Patent A validation |
| LED color | `get_system_status.color_rgb` | Thermochromic output |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-02-17 | Initial specification |
