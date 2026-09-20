# Device 1 (Rev 2.0) — Compact Wireless Audio Terminal
### Fully Repaired, Verified, and Certified Turnkey Handoff Release

[![KiCad 10 DRC](https://img.shields.io/badge/KiCad%20DRC-0%20Violations-brightgreen)](Device1-drc.rpt)
[![KiCad 10 ERC](https://img.shields.io/badge/KiCad%20ERC-0%20Errors-brightgreen)](Device1-erc.rpt)
[![Firmware Build](https://img.shields.io/badge/Firmware-Compiled%20(0%20Errors)-brightgreen)](firmware_build.log)
[![Airtime Margin](https://img.shields.io/badge/Airtime%20Margin-37.5%25%20(Safe)-brightgreen)](RF_REFERENCE_COMPARISON.md)
[![Fabrication](https://img.shields.io/badge/JLCPCB-4--Layer%20SMT%20Ready-blue)](manufacturing/)

---

## 1. Project Overview

**Device 1** is an ultra-compact ($31.0\text{ mm} \times 15.0\text{ mm}$), wearable wireless audio terminal engineered around the **STMicroelectronics STM32WL55CCU6** multi-protocol Sub-GHz wireless dual-core microcontroller. 

This repository contains the **certified Revision 2.0 release**, in which all baseline DRC/ERC errors, trace clearance violations, ground loops, and microphone digital audio routing conflicts have been systematically solved and verified to **0 DRC violations, 0 unconnected pads, and 0 ERC errors**.

---

## 2. Key Specifications & Architectural Highlights

- **Dimensions:** $31.0\text{ mm} \times 15.0\text{ mm} \times 3.5\text{ mm}$ with $1.0\text{ mm}$ corner radius.
- **Audio Capture Subsystem:**
  - Knowles SPH0645LM4H-B 24-bit digital I2S MEMS microphone with bottom acoustic port ($0.50\text{ mm}$ NPTH through-hole on PCB).
  - 16.0 kHz sampling rate, 16-bit linear PCM audio.
  - Dedicated 3-channel non-crossing routing corridors on `B.Cu` referencing continuous solid ground on `In1_Cu`.
- **Speech Compression (IMA ADPCM):**
  - Lossy 4:1 compression engine converting $256\text{ kbps}$ linear PCM into $64.0\text{ kbps}$ ADPCM (4 bits/sample).
  - Validated SNR: **26.92 dB** (pure 440 Hz tone) and **21.61 dB** (speech formants).
- **Sub-GHz RF Transceiver Subsystem:**
  - Integrated transceiver operating in the 868 MHz European ISM band (ETSI EN 300 220 compliant).
  - **150 kbps 2-GFSK** modulation ($F_{dev} = \pm 37.5\text{ kHz}$, $BT = 0.5$, RX channel filter $BW = 234.3\text{ kHz}$).
  - $+14\text{ dBm}$ output power through high-efficiency internal power amplifier (`RFO_HP`).
  - Johanson Technology 0868AT43A0020E ceramic chip antenna with strict $15.0\text{ mm} \times 4.2\text{ mm}$ 4-layer copper keepout.
  - **50.0 Ω Coplanar Waveguide with Ground (CPWG)** on JLCPCB JLC04161H-7628 stackup ($W = 0.29\text{ mm}$, $S = 0.20\text{ mm}$).
  - Switchable 0 Ω link ($R_{\text{ANT}}$ populated, $R_{\text{TEST}}$ unpopulated) to U.FL coaxial port for conducted laboratory RF testing.
- **Power Management:**
  - Hardware P-MOSFET load sharing (Diodes Inc. DMG2305UX) permitting simultaneous operation and charging.
  - Microchip MCP73831 $500\text{ mA}$ linear Li-Ion / LiPo battery charger.
  - Diodes Inc. AP2112K-3.3 $600\text{ mA}$ low-dropout linear regulator ($<55\text{ mV}$ dropout @ $100\text{ mA}$).
  - Complete battery protection circuit (Fortune Semi DW01A + FS8205A dual FET) with dedicated isolated `BATT_NEG` return.

---

## 3. Deliverables Summary

| File / Directory | Description |
| :--- | :--- |
| **[`Device1_COMPLETE_HANDOFF_FIXED.zip`](Device1_COMPLETE_HANDOFF_FIXED.zip)** | **All-in-one complete turnkey handoff ZIP archive** |
| **[`Device1.kicad_pcb`](Device1.kicad_pcb)** | KiCad 10 fully routed 4-layer PCB (**0 DRC violations**) |
| **[`Device1.kicad_sch`](Device1.kicad_sch)** | KiCad 10 complete schematic (**0 ERC errors/warnings**) |
| **[`Device1.kicad_pro`](Device1.kicad_pro)** | KiCad 10 project file with verified design rules |
| **[`Device1_Gerbers.zip`](Device1_Gerbers.zip)** | Upload-ready 4-layer Gerbers + Excellon Drill file for JLCPCB |
| **[`Device1_BOM.csv`](Device1_BOM.csv)** | JLCPCB SMT format Bill of Materials with exact LCSC part numbers |
| **[`DEVICE1_FINAL_BOM.csv`](DEVICE1_FINAL_BOM.csv)** | Master engineering Bill of Materials with manufacturer MPNs |
| **[`Device1_CPL.csv`](Device1_CPL.csv)** | JLCPCB SMT Pick-and-Place file with calibrated rotations |
| **[`Device1-drc.rpt`](Device1-drc.rpt)** | KiCad 10 certified DRC report (**0 violations, 0 unconnected**) |
| **[`Device1-erc.rpt`](Device1-erc.rpt)** | KiCad 10 certified ERC report (**0 errors, 0 warnings**) |
| **[`REPAIR_CHANGELOG.md`](REPAIR_CHANGELOG.md)** | Technical repair changelog documenting all DRC/ERC fixes |
| **[`RF_REFERENCE_COMPARISON.md`](RF_REFERENCE_COMPARISON.md)** | STMicroelectronics MB1848 reference vs Device 1 comparison |
| **[`VALIDATION_REPORT.md`](VALIDATION_REPORT.md)** | Full validation certificate, test benchmarks, and stackup calculations |
| **[`firmware_build.log`](firmware_build.log)** | Compiler build log (Clang ARM Cortex-M4, 0 errors, 0 warnings) |
| **[`firmware/`](firmware/)** | Complete firmware source code, Makefile, linker script, and binaries |
| **[`hardware/`](hardware/)** | KiCad project sources, footprint libraries, and stepwise builder script |
| **[`manufacturing/`](manufacturing/)** | Complete uncompressed Gerbers, NC drill, assembly CPL, and packages |
| **[`validation/`](validation/)** | Link budget analysis, throughput reports, and verification audits |

---

## 4. Verification Evidence

### KiCad Physical DRC Output (`Device1-drc.rpt`)
```
** Drc report for Device1.kicad_pcb **
** Created on 2026-09-20T18:17:38 **
** Report includes: Errors, Warnings, Exclusions **

** Found 0 DRC violations **

** Found 0 unconnected pads **

** Found 0 Footprint errors **
```

### KiCad Schematic ERC Output (`Device1-erc.rpt`)
```
ERC report (2026-09-20T17:58:40, Encoding UTF8)
Report includes: Errors, Warnings

***** Sheet /

 ** ERC messages: 0  Errors 0  Warnings 0
```

### Firmware Memory Utilization (`firmware_build.log`)
```
   text    data     bss     dec     hex filename
   3004      76     684    3764     eb4 Device1_Firmware.elf
Flash: 3,080 bytes / 262,144 bytes (1.17%)
SRAM:    760 bytes /  65,536 bytes (1.16%)
```

---

## 5. How to Re-Verify & Build

### 1. Open Hardware in KiCad 10
```bash
kicad hardware/Device1.kicad_pro
```
To run DRC via CLI:
```bash
kicad-cli pcb drc --severity-all hardware/Device1.kicad_pcb
```

### 2. Build Firmware
Requirements: `arm-none-eabi-gcc` or `clang`, `arm-none-eabi-ld`, `make`.
```bash
cd firmware
make clean
make
```

### 3. Order from JLCPCB
1. Upload `Device1_Gerbers.zip` to JLCPCB Gerber viewer.
2. Select 4-Layer PCB with standard stackup `JLC04161H-7628` (1.6 mm thickness).
3. Under SMT Assembly, upload `Device1_BOM.csv` and `Device1_CPL.csv`. All component rotations in `Device1_CPL.csv` are pre-calibrated to EIA-481 standards.

---

## 6. License & Compliance
- **Design Policy:** 100% Non-Texas Instruments Open Architecture.
- **License:** CERN Open Hardware License v2 - Permissive (CERN-OHL-P).
