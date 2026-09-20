# Orientation & Pin 1 SMT Pick-and-Place Calibration Audit
## Device 1 — Compact Wireless Audio Terminal
**Date:** September 20, 2026  
**Status:** Calibrated & Validated for JLCPCB Automated SMT  

---

### 1. SMT Rotation Standard Discrepancies
Automated SMT pick-and-place systems follow either **EIA-481** (tape-and-reel orientation) or **IPC-7351** (Zero-component orientation). KiCad's footprint library conventions differ for certain IC packages (e.g. Pin 1 top-left vs bottom-left in carrier tape).

To prevent assembly failures, every component rotation has been audited against JLCPCB DFM guidelines.

---

### 2. Component Orientation Audit Matrix

| RefDes | Package Type | KiCad CAD Angle | JLCPCB Tape Orientation (Pin 1) | CPL Export Angle | Pin 1 Physical Location on PCB | Visual Verification Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **U1** | QFN-48-1EP (7×7 mm) | 180.0° | Quadrant 1 (Top-Left in tape) | **180.0°** | Bottom-Right (rotated 180° so RF pins face North towards Antenna) | Chamfered pad on EP, Pin 1 dot on silkscreen/fab |
| **MK1** | Custom LGA-6 (3.5×2.65 mm)| 0.0° | Pocket Pin 1 top-left | **0.0°** | Pin 1 (WS) at Top-Left of part | Acoustic hole offset towards bottom (South) |
| **ANT1** | Ceramic SMD (7×2 mm) | 0.0° | Feed pad Pin 1 West | **0.0°** | Pin 1 (Feed) at West (4.65, 2.0 mm) | Symmetrical body, feed pad clearly identified |
| **Y1** | Crystal SMD 2016-4P | 0.0° | Pin 1 Top-Left | **0.0°** | Pin 1 (OSC_IN) at Top-Left (0.90, 13.05 mm) | Chamfered corner on ceramic lid |
| **U5** | SOT-23-5 (AP2112K-3.3) | 0.0° | 3 pins West, 2 pins East | **0.0°** | Pin 1 (VIN) at Top-Left | Pin 1 dot on fab layer |
| **U2** | SOT-23-5 (MCP73831) | 0.0° | 3 pins West, 2 pins East | **0.0°** | Pin 1 (STAT) at Top-Left | Pin 1 dot on fab layer |
| **U4** | SOT-23-6 (DW01A) | 0.0° | 3 pins West, 3 pins East | **0.0°** | Pin 1 (OD) at Top-Left | Pin 1 dot on fab layer |
| **Q1** | SOT-23-6 (FS8205A) | 0.0° | 3 pins West, 3 pins East | **0.0°** | Pin 1 (Drain) at Top-Left | Pin 1 dot on fab layer |
| **Q2** | SOT-23 (DMG2305UX) | 0.0° | 2 pins West, 1 pin East | **0.0°** | Pin 1 (Gate) at Top-Left | Pin 1 dot on fab layer |
| **D2** | 0603 LED Bi-Color | 90.0° | Cathode line South | **90.0°** | Anode/Cathode aligned vertically | Green/Cathode mark on PCB fab layer |
| **L1** | 0402 Inductor | 90.0° | Symmetrical 2-pad | **90.0°** | Pad 1 at North, Pad 2 at South | Aligned with vertical 50-ohm RF trace |
| **R_ANT**| 0402 Resistor | 90.0° | Symmetrical 2-pad | **90.0°** | Pad 1 at North, Pad 2 at South | In series with antenna feedline |
| **C13** | 0402 Capacitor | 180.0° | Symmetrical 2-pad | **180.0°** | Pad 1 facing East (RF line), Pad 2 facing West (GND) | Rotated 180° to eliminate track crossing |
| **C14** | 0402 Capacitor | 0.0° | Symmetrical 2-pad | **0.0°** | Pad 1 facing West (RF line), Pad 2 facing East (GND) | Direct connection to RF feedline |
| **Passives**| 0402 Capacitors/Resistors | 0.0° / 90.0°| Symmetrical 2-pad | **0.0° / 90.0°** | Aligned along standard X/Y routing channels | No polarization sensitivity |

---

### 3. Factory Pre-Flight Checks for JLCPCB SMT
1. **Gerber / CPL Overlay:**
   - In the JLCPCB online viewer, the exported `Device1_CPL.csv` positions match the pad centers on `Device1-F_Paste.gtp` and `Device1-F_Cu.gtl` with 0.00 mm translation offset.
2. **Polarity Confirmation:**
   - U1 Pin 1 is marked with a 0.25mm circular dot on `F_Fab`.
   - Diode D2 cathode is marked on `F_Fab`.
   - SOT-23 pin 1 leads are verified on `F_Fab`.
