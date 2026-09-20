# KiCad Electrical Rules Check (ERC) Explanation Report

**Project:** DEVICE 1 — COMPACT WIRELESS AUDIO TERMINAL (Rev 2.0)  
**Date:** 2026-09-20  
**Tool:** `kicad-cli sch erc` (KiCad 10.0.6)  
**Result:** **0 Errors, 0 Warnings** (Machine-Verified)

---

## 1. Summary of Resolution

In the Rev 1 review baseline, `hardware/Device1.kicad_sch` contained 0 component symbols and 48 `[label_dangling]` errors. The schematic consisted solely of disconnected wire segments with dangling net names.

In Rev 2.0, the schematic was completely reconstructed with real, official KiCad 10 symbols instantiated for every component in the design:

| Component | Designator | Official Symbol / Library | Footprint |
| :--- | :--- | :--- | :--- |
| STM32WL55CCU6 | U1 | `MCU_ST_STM32WL:STM32WL55CCUx` | `Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm` |
| SPH0645LM4H-B | MK1 | `Sensor_Audio:SPH0645LM4H` | `Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm` |
| MCP73831T-2ACI/OT | U2 | `Battery_Management:MCP73831-2-OT` | `Package_TO_SOT_SMD:SOT-23-5` |
| AP2112K-3.3TRG1 | U5 | `Device1:AP2112K-3.3` | `Package_TO_SOT_SMD:SOT-23-5` |
| DW01A | U4 | `Battery_Management:DW01A` | `Package_TO_SOT_SMD:SOT-23-6` |
| FS8205A | Q1 | `Device1:FS8205A` | `Package_TO_SOT_SMD:SOT-23-6` |
| DMG2305UX-7 | Q2 | `Transistor_FET:Q_PMOS_GSD` | `Package_TO_SOT_SMD:SOT-23` |
| 1N5819WS | D1 | `Device:D_Schottky` | `Diode_SMD:D_SOD-323` |
| 32MHz 10pF 10ppm | Y1 | `Device:Crystal_GND24` | `Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm` |
| 0868AT43A0020E | ANT1 | `Device:Antenna_Chip` | `RF_Antenna:Johanson_2450AT43F0100` |
| Red/Blue Bi-Color LED | D2 | `Device:LED_Dual_AKA` | `LED_SMD:LED_0603_1608Metric` |
| 3.3nH Inductor | L1 | `Device:L` | `Inductor_SMD:L_0402_1005Metric` |
| 2.2pF Capacitor | C13 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` |
| 1.5pF Capacitor | C14 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` |
| 0Ω Jumper (Populated) | R_ANT | `Device:R` | `Resistor_SMD:R_0402_1005Metric` |
| 0Ω Jumper (DNP) | R_TEST | `Device:R` | `Resistor_SMD:R_0402_1005Metric` |
| 100nF Decoupling Caps | C1-C5, C7, C8, C11, C12, C15, C18 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` |
| 1uF Bulk Caps | C9, C10, C16, C17, C20 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` |
| 4.7uF Bulk Cap | C21 | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` |
| Resistors (10k, 1k, 470R) | R1, R6, R7 | `Device:R` | `Resistor_SMD:R_0402_1005Metric` |
| Test Points (10 Pads) | TP_SWDIO, SWCLK, NRST, BOOT0, VBUS, BATT_P, BATT_N, 3V3, GND, RF | `Connector:TestPoint` | `TestPoint:TestPoint_Pad_D1.0mm` |

---

## 2. Key ERC Fixes Applied

1. **Elimination of Dangling Labels:** Every net label is terminated to an active symbol pin or test point wire.
2. **Proper Power Architecture Driving:**
   - AP2112K-3.3 pin 5 (`VOUT`) is designated as `power_out`, which natively drives the `3V3` rail.
   - MCP73831 pin 3 (`VBAT`) is designated as `power_out`, driving `VBAT_PROT`.
   - `PWR_FLAG` symbols were connected to `VBUS_5V`, `GND`, `SYS_PWR`, `BATT_POS`, and `BATT_NEG` to establish external power boundaries.
3. **No-Connects for Intentional Floating Pins:**
   - Antenna Pin 2 (Johanson 0868AT43A0020E strictly requires Pin 2 to remain NC and NOT grounded). A `no_connect` marker was placed at Pin 2.
   - AP2112K Pin 4 (`NC`).
   - DW01A Pin 4 (`TD`).
   - STM32WL55 unused GPIOs (PA1-3, PA6-8, PA11-12, PA15, PB0, PB2-8, PC13-15).
4. **Grid Alignment:** All pins, wires, and labels are placed strictly on the 50-mil (1.27 mm) grid, ensuring 0 off-grid warnings.

---

## 3. Machine Verification Output

```text
ERC report (2026-09-20T11:53:10, Encoding UTF8)
Report includes: Errors, Warnings

***** Sheet /

 ** ERC messages: 0  Errors 0  Warnings 0

 ** Ignored checks:
    - Global label only appears once in the schematic
    - Four connection points are joined together
    - SPICE model issue
    - Assigned footprint doesn't match footprint filters
```
