# VALIDATION & VERIFICATION FINAL ENGINEERING REPORT
## Device 1 — Compact Wireless Audio Terminal (Rev 2.0)

**Project:** Prototype Manufacturing Package Release  
**Target MCU:** STMicroelectronics STM32WL55CCU6TR (UFQFPN48, Dual-core ARM Cortex-M4 @ 48 MHz)  
**Date:** 2026-09-21  
**Status:** **Digitally Validated Fabrication Candidate (Pre-Production Prototype)**  
**Strict Policy:** Open Architecture — 100% Non-Texas Instruments  

---

## 1. Executive Summary

This report documents the comprehensive digital validation, simulation, DRC/ERC audit, and firmware compilation for **Device 1 (Compact Wireless Audio Terminal Rev 2.0)**.

Every design parameter has been verified through authoritative automated design checks, math modeling, and compiler builds:
- **Board Dimensions:** $31.0\,\text{mm} \times 15.0\,\text{mm} \times \sim 3.5\,\text{mm}$ total profile with $1.0\,\text{mm}$ corner radii on `Edge.Cuts`.
- **Audio Capture:** Knowles SPH0645LM4H-B bottom-port I2S digital MEMS microphone, 16.0 kHz sampling rate, 16-bit linear PCM resolution (256 kbps raw), native 0.50 mm NPTH acoustic port through PCB.
- **Audio Compression:** Reference IMA ADPCM encoder delivering 4:1 lossy speech compression ($16\text{ kHz} \times 4\text{ bits/sample} = \mathbf{64\text{ kbps}}$). 128 samples per 8.0 ms frame compressed into 64 packed nibble bytes. SNR = 32.53 dB (440 Hz Sine), 27.43 dB (Speech Formants).
- **Sub-GHz Radio:** Integrated Sub-GHz radio core configured for 868.0 MHz carrier, 2-GFSK modulation ($BT = 0.5$, $F_{dev} = 37.5\,\text{kHz}$), authoritative PHY data rate of **150,000 bps (150 kbps)**, +14 dBm transmit power into a 7-element discrete switchless front-end.
- **RF Matching & Filter:** 7-element discrete switchless network (`L1` 3.3nH, `L2` 47nH, `L3` 18nH, `C13` 2.2pF, `C14` 1.5pF, `C22` 1.5pF, `C23` 1.5pF) supported by ST AN5457 Rev 3 and Semtech AN1200.40.
- **Antenna:** Johanson Technology 0868AT43A0020E ceramic chip antenna ($7.00 \times 2.00 \times 0.80\,\text{mm}$ body outline) on custom verified land pattern `Johanson_0868AT43A0020E_CUSTOM`, with a $15.00 \times 4.30\,\text{mm}$ 4-layer copper keepout window.
- **RF Transmission Line:** $50.0\,\Omega$ Coplanar Waveguide with Ground (CPWG), $0.28\,\text{mm}$ trace width, $0.20\,\text{mm}$ side ground gap, referencing unbroken Layer 2 (`In1_Cu`) ground plane on JLCPCB JLC04161H-7628 stackup.
- **Power Architecture:** Discrete P-MOSFET load sharing (DMG2305UX), Diodes Inc AP2112K-3.3 600mA low-noise LDO, Microchip MCP73831 500mA linear Li-Ion charger, Fortune Semi DW01A + FS8205A battery protection, JCET 1N5819WS Schottky diode.
- **Component Accounting:** 50 total PCB footprints, 40 SMT component footprints, 1 DNP test jumper (`R_TEST`), and **39 populated SMT components**.
- **Firmware:** Clean build with Clang target `armv7em-none-eabi` and GNU `arm-none-eabi-ld` with zero compiler warnings and zero linker warnings (no suppression flags).
- **Physical Test Disclosure:** Pre-production digital verification is complete. Physical RF harmonic emissions, antenna return loss ($S_{11}$), receiver sensitivity, and field range require physical laboratory instrumentation and bench testing on prototype hardware.

---

## 2. Automated Test Results & Benchmarks

### 2.1 IMA ADPCM Codec Benchmark (`firmware/tools/test_adpcm`)
- **Test 1: Silence Tracking:** PASSED (Mean Error = 0.000, Max Error = 0.000, zero drift)
- **Test 2: 440 Hz Sine Wave:** PASSED (Reconstructed SNR = **32.53 dB**, target > 20 dB)
- **Test 3: Speech Formant Simulation:** PASSED (Reconstructed SNR = **27.43 dB**, target > 18 dB)
- **Test 4: Low-Amplitude Noise:** PASSED (Stable tracking without accumulator runaway)
- **Test 5: Extreme Clipping & Dynamic Range:** PASSED (Clean saturation without arithmetic overflow)
- **Compression Ratio:** Exactly 4:1 (32,000 raw PCM bytes/s $\to$ 8,000 compressed bytes/s = 64 kbps)

### 2.2 Stackup & RF Transmission Line Calculation
- **Stackup Profile:** JLCPCB JLC04161H-7628 (1.6 mm thickness, 1 oz copper)
- **Dielectric Thickness (L1 to L2):** 0.20 mm (7628 Prepreg)
- **Dielectric Constant ($\epsilon_r$):** 4.34 @ 868 MHz
- **CPWG Trace Width ($W$):** 0.28 mm
- **Ground Clearance Gap ($S$):** 0.20 mm
- **Characteristic Impedance ($Z_0$):** **50.0 Ω**
- **Antenna Keepout:** $15.00\,\text{mm} \times 4.30\,\text{mm}$, 100% stripped of copper across all 4 layers.

### 2.3 DRC & ERC Electrical Design Rules
- **KiCad Schematic ERC (`validation/ERC_FINAL.txt`):** **0 errors, 0 warnings**.
- **KiCad PCB Physical DRC (`validation/DRC_FINAL.txt`):**
  - DRC Violations: **0 violations** (with zones refilled).
  - Unconnected Items: **0 unconnected items / nets**.
  - Footprint Errors: **0 footprint errors**.
  - Minimum Component Clearance: $\ge 0.200\,\text{mm}$.
  - Via Dimensions: $0.25\,\text{mm}$ drill / $0.45\,\text{mm}$ pad.
  - MCU Thermal Vias: 3×3 array of $0.30\,\text{mm}$ drill / $0.60\,\text{mm}$ pad under exposed pad.

### 2.4 Firmware Compilation & Memory Footprint (`validation/FIRMWARE_BUILD_FINAL.txt`)
- **Toolchain:** Clang target `armv7em-none-eabi` + GNU ARM Linker (`arm-none-eabi-ld`)
- **Compiler Warnings:** **0**
- **Linker Warnings:** **0** (Suppression `--no-warn-rwx-segments` removed; zero RWX segments confirmed via `readelf -l`)
- **Flash Utilization:** 3,748 bytes / 262,144 bytes (**1.43%**)
- **SRAM Utilization:** 1,008 bytes / 65,536 bytes (**1.54%**)
- **Packet Structure:** 72-byte payload struct (8-byte header + 64-byte audio) packed with `#pragma pack(push, 1)`.
- **OTA Frame Size:** 80 bytes (640 bits total including 4B preamble, 2B sync, 72B payload, 2B CRC).
- **Timing & Airtime Margin:** **38.04% timing margin** (3.043 ms idle/processing margin in 8.000 ms frame @ 150 kbps).

---

## 3. Manufacturing Consistency Summary

| Metric | Measured Value |
| :--- | :--- |
| **Total PCB Footprints** | 50 (40 SMT + 10 Test Points) |
| **Actual SMT Footprints** | 40 |
| **DNP Footprints** | 1 (`R_TEST` 0R jumper) |
| **Populated SMT Placements** | **39 components** |
| **BOM Populated Quantity** | **39 components** |
| **CPL Placement Rows** | **39 rows** |
| **BOM / CPL Consistency** | **100% 1:1 match (0 missing parts, 0 unpopulated placements)** |
| **Texas Instruments Components** | **0% across entire BOM** |

---

## 4. Required Physical Verification Tests

The following parameters cannot be certified digitally and must be validated on physical prototype units:
1. **$S_{11}$ Return Loss & Resonant Frequency:** Measurement of Johanson antenna input impedance via VNA on populated PCB with plastic enclosure / casing proximity.
2. **Conducted Output Power:** Measurement at `TP_RF` with spectrum analyzer/power meter ($+14.0\,\text{dBm} \pm 1.0\,\text{dB}$ target).
3. **Harmonic Suppression:** Verification of 2nd harmonic ($1736\,\text{MHz} < -36\,\text{dBm}$) and 3rd harmonic ($2604\,\text{MHz} < -36\,\text{dBm}$) to confirm ETSI EN 300 220 compliance.
4. **Modulation Spectrum & Occupied Bandwidth:** 2-GFSK spectral mask verification at 150 kbps ($\le 250\,\text{kHz}$ 99% OBW).
5. **Receiver Sensitivity ($S_{RX}$):** Verification of $-102\,\text{dBm}$ to $-104\,\text{dBm}$ sensitivity at $BER = 10^{-3}$ on differential LNA path.
6. **Physical Line-of-Sight Range:** Real-world field verification of target $400\text{–}500\,\text{m}$ clear line-of-sight voice reception.
7. **Battery Discharge Profile:** Measured streaming endurance with selected 120 mAh 1S LiPo under continuous TX.
8. **Audio THD+N & Intelligibility:** Acoustic chamber verification of SPH0645 microphone frequency response and IMA ADPCM intelligibility.

---

## 5. Engineering Conclusion

Device 1 Rev 2.0 is a **digitally validated fabrication candidate**. All electrical rules, design rules, timing budgets, and manufacturing outputs are consistent, rule-checked, and synchronized. Physical RF bring-up and system testing remain required on manufactured hardware.
