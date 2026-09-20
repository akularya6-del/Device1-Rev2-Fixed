# ENGINEERING CORRECTIONS TO DEVICE1_ENGINEERING_PLAN.md

This document records every material engineering correction made during execution, citing primary evidence, datasheets, reference designs, and manufacturability constraints.

---

### CORRECTION 001: Audio Microphone Selection & Footprint Compatibility
- **Plan statement:** Proposed TDK ICS-43434 or Knowles SPH0645LM4H-B or TDK T5848.
- **Evidence:** 
  1. TDK InvenSense T5848 (MMICT5848-00-012) requires a 1.8V supply (1.62V–1.98V max) according to its datasheet; our system supply is 3.3V. Using T5848 directly on 3.3V would exceed absolute maximum ratings and cause permanent device destruction.
  2. TDK ICS-43434 is marked Last-Time-Buy (discontinued).
  3. Knowles SPH0645LM4H-1 / SPH0645LM4H and CUI Devices CMM-3526D-261-I2S-TR are 3.3V-compatible (1.6V–3.6V operating range) 24-bit I2S digital MEMS microphones.
  4. Crucially, Knowles SPH0645LM4H, TDK ICS-43434, and CUI CMM-3526D share the exact same 3.50 mm × 2.65 mm LGA-6 package, landing pad layout, acoustic port diameter (0.50 mm), and pinout:
     - Pin 1: WS (LRCLK)
     - Pin 2: SEL / LR
     - Pin 3: GND
     - Pin 4: BCLK / SCK
     - Pin 5: VDD (3.3V)
     - Pin 6: DATA / SD
- **Problem:** Ambiguity in microphone selection risked choosing a 1.8V-only part (T5848) or an un-procurable obsolete part.
- **Correction:** Locked the physical PCB land pattern to the industry-standard `Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm` footprint with a 0.50 mm plated through-hole acoustic port on the PCB. The primary BOM component is locked to **Knowles SPH0645LM4H-1** with direct drop-in alternates **CUI CMM-3526D-261-I2S-TR** and **InvenSense ICS-43434**.
- **Effect on design:** 100% electrical compatibility with 3.3V VDD, verified 24-bit I2S timing with STM32WL SPI2/I2S master, and robust multi-vendor procurement resilience.

---

### CORRECTION 002: Power Architecture — 3.3V LDO Voltage Regulator Upgrade
- **Plan statement:** Proposed Torex XC6206P332MR (200 mA max) or Microchip MIC5205.
- **Evidence:** 
  1. STM32WL55 peak instantaneous current during RF transmit (+15 dBm to +22 dBm) reaches 87 mA to 120 mA. Adding CPU (10 mA), MEMS Mic (0.6 mA), bi-color LED (4 mA), and transient charging/switching spikes yields peak currents up to 140–150 mA.
  2. Torex XC6206 has a rated limit of 200 mA with high dropout (~400 mV at 200 mA) and notoriously sluggish transient load response, risking severe VDD droop and MCU brownout during RF packet transmission.
  3. Diodes Incorporated **AP2112K-3.3TRG1** provides 600 mA continuous output capability (5x headroom), ultra-low dropout (250 mV at 600 mA, <55 mV at 100 mA), fast transient response, low quiescent current (55 µA), and is fully stable with standard low-ESR 0402/0603 ceramic capacitors.
  4. AP2112K-3.3TRG1 is an active non-TI part readily stocked on LCSC (C52994) and JLCPCB.
- **Problem:** XC6206 is marginal on current, slow on RF transients, and drops out prematurely as the LiPo cell discharges below 3.6V.
- **Correction:** Replaced XC6206 with **Diodes Inc. AP2112K-3.3TRG1** in SOT-23-5.
- **Effect on design:** Stable 3.3V rail down to 3.35V cell voltage, zero risk of brownout on RF transmit bursts, 600 mA current margin.

---

### CORRECTION 003: Power Topology — Implementation of Dedicated Load Sharing
- **Plan statement:** Proposed a linear sequence: Battery -> DW01A protection -> MCP73831 charger -> LDO.
- **Evidence:** 
  1. Microchip MCP73831 is a standalone CC/CV linear charger without built-in power-path management.
  2. If the system load is connected directly in parallel with the battery during charging, the system draw prevents the charger from detecting the C/10 charge termination threshold, causing prolonged trickle/float charging that damages LiPo chemistry and generates excess heat.
  3. Microchip Application Note AN1149 outlines the standard non-TI discrete load-sharing circuit using a P-channel MOSFET, Schottky diode, and pull-up resistor.
- **Problem:** Operating or charging without load sharing compromises battery safety and cycle life.
- **Correction:** Implemented hardware load sharing:
  - 5V USB charging input connects to MCP73831 VDD and anode of Schottky diode D_CHG (1N5819WS).
  - P-Channel MOSFET Q2 (DMG2305UX) gate connects to 5V USB (with 100 kΩ pull-down to GND).
  - Source connects to LDO VIN; Drain connects to VBAT_PROT.
  - When 5V USB is plugged in: Gate is high (5V), Q2 turns OFF, disconnecting battery from system load. System runs off 5V through D_CHG, allowing MCP73831 to cleanly charge and terminate.
  - When 5V USB is unplugged: Gate is pulled low, Q2 turns ON (Rds_on < 30 mΩ), powering LDO with negligible voltage drop (<5 mV).
- **Effect on design:** Safe, compliant LiPo charging, zero battery degradation during plug-in, seamless power source handover.

---

### CORRECTION 004: RF Front-End Architecture — ST Reference Design Integration
- **Plan statement:** Proposed: MCU RF_OUT -> simple Pi-matching network -> chip antenna.
- **Evidence:** 
  1. STM32WL55 does not have a single combined RF_OUT pin. It features separate high-power output (`RFO_HP`, pin 23), low-power output (`RFO_LP`, pin 22), and differential balanced receiver inputs (`RFI_P`, pin 20; `RFI_N`, pin 21).
  2. A direct connection of a simple Pi network to one pin leaves the receiver disconnected and violates the required conjugate differential impedance match for RFI_P/N.
  3. STMicroelectronics reference designs (MB1848 / STDES-WL5U4IHH) for the STM32WL in UFQFPN48 specify the ST Integrated Passive Device **BALFHB-WL-02D3** (LCSC C5350082).
  4. BALFHB-WL-02D3 integrates the PA matching, differential Rx balun, and 5th-order harmonic filter into a single 4-layer-matched IPD specifically designed for 868 MHz on STM32WL QFN48.
- **Problem:** The original plan omitted the receiver balun, PA harmonic filtering, and differential front-end matching.
- **Correction:** Implemented the ST reference design front-end:
  - Connect `RFO_HP` (pin 23), `RFI_P` (pin 20), `RFI_N` (pin 21) directly to `BALFHB-WL-02D3`.
  - Connect `BALFHB-WL-02D3` 50 Ω output port through a tunable Pi-network (0402 C-L-C).
  - Provide a switchable 0 Ω jumper path (R_ANT = 0 Ω, R_TEST = DNP) leading to both the Johanson 0868AT43A0020001E ceramic chip antenna and an optional U.FL coaxial test connector for conducted RF measurements without stubs.
- **Effect on design:** Rigorously matches ST RF architecture, maximizes RX sensitivity, guarantees harmonic compliance, enables conducted RF testing on Rev 1.

---

### CORRECTION 005: Low-Speed Crystal (LSE) Elimination
- **Plan statement:** Retained 32.768 kHz LSE crystal with placeholder 12 pF capacitors.
- **Evidence:** 
  1. Device 1 is an audio streaming transmitter that activates on demand to stream voice packets and receive a rapid A/B/C/D return command.
  2. It does not require a calendar Real-Time Clock (RTC).
  3. Sub-GHz packet timing and intervals are derived directly from the radio timer clocked by the high-precision 32 MHz HSE crystal.
  4. The 32.768 kHz crystal consumes ~3.2 mm × 1.5 mm of PCB space, adds two external load capacitors, introduces startup failure risk, and increases BOM count.
- **Problem:** Unnecessary component consuming critical wearable PCB area with zero functional benefit.
- **Correction:** Eliminated the 32.768 kHz crystal. Low-power standby/sleep wake-up uses the STM32 internal low-speed RC oscillator (LSI, 32 kHz ±5%), while all RF and audio timing uses the calibrated 32 MHz HSE.
- **Effect on design:** Frees 8 mm² of board space, eliminates 3 BOM lines, simplifies routing, improves reliability.

---

### CORRECTION 006: HSE Crystal Load Capacitors
- **Plan statement:** Unclear whether external load capacitors should be placed for the 32 MHz crystal.
- **Evidence:** 
  1. ST Application Note AN5430 ("Precise HSE frequency and startup time tuning for STM32 wireless MCUs") specifies that the STM32WL55 includes internal programmable capacitor banks on `OSC_IN` and `OSC_OUT` (programmable from 0 pF to ~30 pF with 0.4 pF steps).
  2. Adding external discrete capacitors in parallel with internal caps restricts tuning range and introduces trace parasitic capacitance.
- **Problem:** External fixed capacitors could shift oscillator resonant frequency and prevent accurate RF carrier synthesis.
- **Correction:** Omitted discrete load capacitors on Y1 (Murata XRCGB32M000F3M00R0, 32 MHz, 6 pF rated CL). The firmware trims the internal capacitor bank register `RCC_EXTCFGR` during bring-up. Added 0402 placeholder footprints to ground marked DNP (Do Not Populate) as a fallback.
- **Effect on design:** Clean, parasitic-free crystal layout, software-tunable carrier accuracy (<5 ppm).
