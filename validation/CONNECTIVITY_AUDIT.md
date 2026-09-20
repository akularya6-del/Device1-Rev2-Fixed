# Connectivity & Signal Integrity Audit
## Device 1 — Compact Wireless Audio Terminal
**Date:** September 20, 2026  
**Status:** Complete Audit Passed — Strictly Non-TI Architecture  

---

### 1. Power Distribution Network (PDN) Audit

#### 1.1 Four-Layer Stackup Allocation
- **Layer 1 (F.Cu):** Top Signals, 50-Ohm RF CPWG Transmission Line, SMD Component Lands, Top Ground Flood.
- **Layer 2 (In1.Cu):** Continuous Solid Ground Plane (`GND`). Zero splits underneath high-speed signals or RF transmission lines.
- **Layer 3 (In2.Cu):** Continuous Solid 3.3V Power Plane (`3V3`). Low-inductance power delivery to MCU core and peripherals.
- **Layer 4 (B.Cu):** Bottom Return Ground Flood, Low-Frequency Control Routing, Pogo-Pin Test Pads.

#### 1.2 Power Rails & Decoupling Strategy
| Power Net | Source | Destination Components | Bypass Capacitors | Transient Drop / Inductance Mitigations |
| :--- | :--- | :--- | :--- | :--- |
| `VBUS_5V` | USB / External 5V Header | U2 (MCP73831 Pin 4), Q2 (DMG2305UX Gate/Source) | `C18` (0.1 uF 50V X7R) | ESD protection rating, direct trace to charger input |
| `VBAT_PROT`| 1S LiPo via Protection | U2 (MCP73831 Pin 3), Q2 (DMG2305UX Drain), U4 (DW01A) | `C17` (1.0 uF 25V X5R) | Short low-impedance connection to battery protection MOSFETs |
| `SYS_PWR` | Power-Path Output | U5 (AP2112K-3.3 Pins 1 & 3), U1 (VDD/SMPS Pin 24) | `C20` (1.0 uF), `C9` (1.0 uF), `C10` (1.0 uF) | Auto-switching load sharing: USB powered when connected, LiPo otherwise |
| `3V3` | AP2112K-3.3 (Pin 5) | U1 (STM32WL VDD pins), MK1 (SPH0645 Pin 5) | `C21` (4.7 uF Bulk), `C1`-`C8`, `C11`, `C15`, `C16` (0.1 uF / 1.0 uF) | Solid Layer 3 power plane with drop vias adjacent to each VDD pin |
| `GND` | System Common | All Subsystems, Exposed Pad (EP), Antenna ground | 3×3 Thermal Via Array under U1 EP | Continuous reference plane on Layer 2; low impedance RF return path |

---

### 2. High-Frequency RF Transmission Path Audit (868 MHz)

```
[STM32WL55CCU6 Pin 23: RFO_HP]
          |
     (0.29 mm CPWG)
          |
    [Pi-Filter Node 1] <---> [C13: 2.2pF Shunt to GND]
          |
     [L1: 3.3nH Series]
          |
    [Pi-Filter Node 2] <---> [C14: 1.5pF Shunt to GND]
          |
    [R_ANT: 0R Series Jumper]
          |
     (0.29 mm CPWG)
          |
[Johanson 0868AT43A0020E Ceramic Chip Antenna Pad 1]
```

- **Target Impedance:** 50.0 Ω ± 2.0 Ω.
- **Trace Geometry:** 0.29 mm trace width, 0.20 mm gap to top ground flood, 0.20 mm dielectric thickness to Layer 2 solid ground plane.
- **Substrate:** FR4 Core / Prepreg, εr = 4.34 at 868 MHz (JLCPCB JLC04161H-7628 stackup).
- **Discontinuities:** 0 sharp 90° bends; smooth straight vertical run along X=5.25 mm.
- **Return Current:** Continuous uninterrupted copper on Layer 2 immediately beneath the trace.

---

### 3. Audio & Control Signal Connectivity

| Signal Net | Source Pin | Destination Pin | Protocol / Function | Routing Layer | Trace Width | Length / Characteristics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MIC_WS` | U1 Pin 32 (PB12) | MK1 Pin 1 (WS) | I2S Word Select (16 kHz Frame Clock) | B.Cu / F.Cu | 0.15 mm | Matched length, routed in shielded corridor |
| `MIC_SCK` | U1 Pin 17 (PA9) | MK1 Pin 4 (SCK) | I2S Bit Clock (512 kHz Master Clock) | B.Cu / F.Cu | 0.15 mm | Low crosstalk, isolated from analog RF |
| `MIC_SD` | MK1 Pin 6 (DATA) | U1 Pin 33 (PA10) | I2S Serial Data In | B.Cu / F.Cu | 0.15 mm | Direct connection to STM32WL I2S2 DMA engine |
| `OSC_IN` | Y1 Pin 1 | U1 Pin 26 (OSC_IN) | 32.000 MHz HSE Oscillator Input | F.Cu | 0.20 mm | Shortest possible trace (<2.5 mm), zero vias |
| `OSC_OUT` | Y1 Pin 3 | U1 Pin 27 (OSC_OUT) | 32.000 MHz HSE Oscillator Output | F.Cu | 0.20 mm | Symmetrical to OSC_IN, guarded by GND vias |
| `SWDIO` | U1 Pin 36 (PA13) | `TP_SWDIO` (B.Cu) | ARM CoreSight Serial Wire Data | B.Cu | 0.20 mm | Pogo-pin programming pad |
| `SWCLK` | U1 Pin 42 (PA14) | `TP_SWCLK` (B.Cu) | ARM CoreSight Serial Wire Clock | B.Cu | 0.20 mm | Pogo-pin programming pad |
| `NRST` | U1 Pin 18 (NRST) | `C12` / `TP_NRST` | Hardware Reset (Active Low) | F.Cu / B.Cu | 0.15 mm | Filtered with 100nF to GND |
| `BOOT0` | U1 Pin 19 (BOOT0) | `R1` (10k to GND) | Hardware Bootloader Select | F.Cu / B.Cu | 0.15 mm | Pulled low by default; test point for bootloader |
| `LED_R` | U1 Pin 12 (PB0) | `R6` (1k) -> `D2` | Visual Indicator Red | F.Cu / B.Cu | 0.15 mm | Low-battery & error states |
| `LED_B` | U1 Pin 13 (PB1) | `R7` (470R) -> `D2` | Visual Indicator Blue | F.Cu / B.Cu | 0.15 mm | Streaming heartbeat & ACK/Command feedback |
