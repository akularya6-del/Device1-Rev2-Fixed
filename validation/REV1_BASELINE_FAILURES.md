# REV 1 BASELINE FAILURE REPORT
## Device 1 — Compact Wireless Audio Terminal
**Date:** September 20, 2026  
**Auditor:** Repair & Validation Engineer  
**Status:** REJECTED — Independent Review Verified Multiple Critical Blockers  

---

### Executive Summary of Failures
An exhaustive, machine-verified audit of the existing Rev 1 delivery package in `/Users/racoon/Documents/CHEATING/Device1/` was conducted prior to making any repairs. Every issue reported by the independent review was tested and confirmed:

1. **Schematic is Empty of Real Symbols:** `Device1.kicad_sch` contains **zero (0) component symbols**. It contains only raw wire segments and labels, rendering the previous ERC completely invalid.
2. **ERC Reports 48 Critical Errors:** When evaluated by `kicad-cli sch erc`, the schematic yields **48 `[label_dangling]` errors**.
3. **Severe PCB Power Net Shorts:** DRC detects **16 critical DRC violations**, including:
   - `BATT_NEG` shorted directly to `3V3` via Q1 pad 4 and a 3V3 through-hole via.
   - `SYS_PWR` shorted directly to `3V3` via C9 pad 1 and a 3V3 track/via.
   - `GND` shorted directly to `3V3` via U2 pad 5 and a 3V3 via.
4. **43 Unrouted / Disconnected Connections:** Despite claims of completion, **43 unconnected items** exist across every critical subsystem (I2S audio lines, crystal pins, SWD, battery, charger, LEDs, and power buses).
5. **Firmware Contains Comment-Only Hardware Stubs:** Peripheral drivers (`audio_i2s.c`, `subghz_radio.c`, `power_mgr.c`, `led_ui.c`) contain placeholder comments (`/* In actual HW: ... */`) instead of real register/HAL initialization.
6. **Linker Script Emits RWX Warning:** The GNU ARM Linker emits `warning: Device1_Firmware.elf has a LOAD segment with RWX permissions`.
7. **Audio Throughput Calculation Error:** The previous documentation claimed $16 \text{ kHz} \times 4\text{-bit} = 32 \text{ kbps}$, when in fact $16,000 \times 4 = 64 \text{ kbps}$. At 100 kbps GFSK, payload transmission requires 80% channel airtime, leaving inadequate margin (< 14%) for the 500 µs RX return command window.
8. **Antenna Footprint & Pinout Error:** The board used a 2.45 GHz Johanson footprint (`2450AT43F0100`) with Pin 2 tied to `GND`. For the 868 MHz antenna (`0868AT43A0020E`), Pin 2 is strictly **NC (No Connect)** / mechanical anchor and must never be grounded.
9. **Pinout Discrepancy:** `hardware_config.h` defined `SWCLK` on PA14 (Pin 42), but the accompanying comment incorrectly labeled it `PA4`.

---

### 1. Schematic & Electrical Rules Check (ERC) Audit
- **File:** `hardware/Device1.kicad_sch`
- **Total Components Found:** **0** (Zero symbols instantiated in `(lib_symbols)`)
- **Total Nets:** 24 labels with disconnected wire stubs
- **ERC Output (`kicad-cli sch erc`):**
  ```
  Found 48 violations
  ERC messages: 48  Errors 48  Warnings 0
  ```
- **Violations List:**
  - `[label_dangling]`: Label not connected @ (25.40, 25.40 mm) '3V3'
  - `[label_dangling]`: Label not connected @ (25.40, 38.10 mm) 'GND'
  - `[label_dangling]`: Label not connected @ (25.40, 50.80 mm) 'VBUS_5V'
  - `[label_dangling]`: Label not connected @ (25.40, 63.50 mm) 'VBAT_PROT'
  - `[label_dangling]`: Label not connected @ (25.40, 76.20 mm) 'BATT_POS'
  - `[label_dangling]`: Label not connected @ (25.40, 88.90 mm) 'BATT_NEG'
  - `[label_dangling]`: Label not connected @ (25.40, 101.60 mm) 'SYS_PWR'
  - `[label_dangling]`: Label not connected @ (25.40, 114.30 mm) 'CHG_STAT'
  - `[label_dangling]`: Label not connected @ (76.20, 25.40 mm) 'MIC_WS'
  - `[label_dangling]`: Label not connected @ (76.20, 38.10 mm) 'MIC_SCK'
  - `[label_dangling]`: Label not connected @ (76.20, 50.80 mm) 'MIC_SD'
  - `[label_dangling]`: Label not connected @ (127.00, 25.40 mm) 'RFO_HP'
  - `[label_dangling]`: Label not connected @ (127.00, 38.10 mm) 'RFI_P'
  - `[label_dangling]`: Label not connected @ (127.00, 50.80 mm) 'RFI_N'
  - `[label_dangling]`: Label not connected @ (127.00, 63.50 mm) 'RF_50OHM'
  - `[label_dangling]`: Label not connected @ (127.00, 76.20 mm) 'ANT_FEED'
  - `[label_dangling]`: Label not connected @ (177.80, 25.40 mm) 'OSC_IN'
  - `[label_dangling]`: Label not connected @ (177.80, 38.10 mm) 'OSC_OUT'
  - `[label_dangling]`: Label not connected @ (228.60, 25.40 mm) 'SWDIO'
  - `[label_dangling]`: Label not connected @ (228.60, 38.10 mm) 'SWCLK'
  - `[label_dangling]`: Label not connected @ (228.60, 50.80 mm) 'NRST'
  - `[label_dangling]`: Label not connected @ (228.60, 63.50 mm) 'BOOT0'
  - `[label_dangling]`: Label not connected @ (228.60, 76.20 mm) 'LED_R'
  - `[label_dangling]`: Label not connected @ (228.60, 88.90 mm) 'LED_B'
  *(Repeated at destination endpoints, totaling 48 errors)*

---

### 2. PCB Physical & Design Rules Check (DRC) Audit
- **File:** `hardware/Device1.kicad_pcb`
- **Footprints Placed:** 34 SMT footprints on Top + 9 Test Points on Bottom
- **DRC Summary (`kicad-cli pcb drc`):**
  ```
  Found 16 DRC violations
  Found 43 unconnected items
  ```

#### 2.1 Critical Power Shorts
1. **`BATT_NEG` ↔ `3V3` Short:**
   - Pad 4 `[BATT_NEG]` of Q1 (FS8205A) @ (8.638, 25.650 mm)
   - Via `[3V3]` on F.Cu - B.Cu @ (9.200, 26.200 mm)
   - *Direct physical copper overlap between battery negative and regulated 3.3V bus.*
2. **`SYS_PWR` ↔ `3V3` Short (Via):**
   - Via `[3V3]` on F.Cu - B.Cu @ (6.750, 17.800 mm)
   - Pad 1 `[SYS_PWR]` of C9 @ (7.020, 17.500 mm)
   - *Shorts unregulated system battery power directly to 3.3V LDO output.*
3. **`GND` ↔ `3V3` Short:**
   - Via `[3V3]` on F.Cu - B.Cu @ (13.200, 20.000 mm)
   - Pad 5 `[GND]` of U2 (MCP73831) @ (13.138, 19.850 mm)
   - *Dead short from 3.3V power plane to system ground.*
4. **`SYS_PWR` ↔ `3V3` Short (Track):**
   - Pad 1 `[SYS_PWR]` of C9 on F.Cu @ (7.020, 17.500 mm)
   - Track `[3V3]` on F.Cu @ (6.750, 15.938 mm)

#### 2.2 Hole-to-Copper & Clearance Violations
- `[hole_clearance]`: Pad 5 `[GND]` of U2 to Via `[3V3]` (actual 0.0000 mm; required 0.25 mm)
- `[hole_clearance]`: Pad 1 `[SYS_PWR]` of C9 to Via `[3V3]` (actual 0.0000 mm; required 0.25 mm)
- `[hole_clearance]`: Pad 4 `[BATT_NEG]` of Q1 to Via `[3V3]` (actual 0.1031 mm; required 0.25 mm)
- `[clearance]`: Track `[3V3]` on F.Cu to Pad 4 `[BATT_NEG]` of Q1 (actual 0.1531 mm; required 0.20 mm)
- `[solder_mask_bridge]`: 4 occurrences where solder mask bridges different nets without minimum dam width.
- `[starved_thermal]`: 3 occurrences where thermal relief spoke count is < 2 (U2 GND, U1 GND, Y1 GND).

#### 2.3 Unconnected Nets (43 Items)
- **Audio Subsystem:**
  - `MIC_WS`: MK1 pad 1 (6.60, 27.44) ↔ U1 pin 32 (4.06, 13.25)
  - `MIC_SCK`: MK1 pad 4 (8.40, 28.26) ↔ U1 pin 17 (8.25, 9.06)
  - `MIC_SD`: MK1 pad 6 (7.50, 27.44) ↔ U1 pin 33 (4.06, 13.75)
- **Crystals & Clocking:**
  - `OSC_IN`: Y1 pad 1 (0.90, 13.05) ↔ U1 pin 26 (4.06, 10.25)
  - `OSC_OUT`: Y1 pad 3 (2.30, 11.95) ↔ U1 pin 27 (4.06, 10.75)
- **Programming & Control:**
  - `SWDIO`: U1 pin 36 (4.06, 15.25) ↔ `TP_SWDIO` (2.80, 22.80)
  - `SWCLK`: U1 pin 42 (7.25, 15.94) ↔ `TP_SWCLK` (5.50, 22.80)
  - `NRST`: U1 pin 18 (7.75, 9.06) ↔ C12 pad 1 ↔ `TP_NRST` (9.50, 24.50)
  - `BOOT0`: U1 pin 19 (7.25, 9.06) ↔ R1 pad 1 ↔ `TP_BOOT0` (3.50, 7.80)
- **Power Management & Protection:**
  - `SYS_PWR`: U5 pin 1 & 3 ↔ Q2 pin 2 ↔ C20 ↔ C9 ↔ C10 ↔ U1 pin 24
  - `VBAT_PROT`: U2 pin 3 ↔ Q2 pin 3 ↔ C17 pad 1 ↔ U4 pin 5
  - `VBUS_5V`: U2 pin 4 ↔ Q2 pin 1 ↔ C18 pad 1 ↔ `TP_VBUS`
  - `BATT_NEG`: U4 pins 1,3,6 ↔ Q1 pins 2,3,4,5 ↔ `TP_BATT_N`
  - `BATT_POS`: U4 pin 5 ↔ `TP_BATT_P`
  - `3V3`: Multiple bypass caps (C11, C15, C16) not connected to plane
- **User Interface:**
  - `LED_R`: U1 pin 12 (10.94, 9.75) ↔ R6 ↔ D2 pad 1
  - `LED_B`: U1 pin 13 (10.25, 9.06) ↔ R7 ↔ D2 pad 2

---

### 3. Firmware Source & Build Audit
- **Files Inspected:**
  - `firmware/src/main.c`
  - `firmware/src/startup.c`
  - `firmware/audio/audio_i2s.c`
  - `firmware/radio/subghz_radio.c`
  - `firmware/power/power_mgr.c`
  - `firmware/ui/led_ui.c`
  - `firmware/stm32wl55ccu6.ld`
- **Compiler:** Clang (`-target armv7em-none-eabi`) + GNU `arm-none-eabi-ld`
- **Build Status:** Builds, but contains major blockers:
  1. **Hardware Stubs:**
     - `audio_i2s_init()`: Contains no register writes; only comments describing steps.
     - `subghz_radio_init()`: Sets a boolean flag without configuring the SX126x/SUBGHZSPI registers.
     - `subghz_radio_send_frame()`: Writes to an internal memory buffer; lacks actual SPI transmission to radio FIFO.
     - `subghz_radio_receive_ack()`: Stubbed return `false`; does not configure RX or read FIFO.
     - `power_mgr_update()`: Hardcodes a static 3700 mV variable; no ADC1 conversions.
     - `system_clock_config()`: Empty stub; MCU runs on default MSI oscillator instead of HSE 32 MHz.
  2. **Linker Warning:**
     `arm-none-eabi-ld: warning: Device1_Firmware.elf has a LOAD segment with RWX permissions`
     Caused by assigning executable and writable attributes to the same memory segment.

---

### 4. Audio Throughput & Radio Airtime Math Error
- **Error in Rev 1:** Documented audio bitrate was $16 \text{ kHz} \times 4\text{-bit} = 32 \text{ kbps}$.
- **Correct Audio Math:**
  $$16,000 \text{ samples/second} \times 4 \text{ bits/sample} = 64,000 \text{ bps} = 64.0 \text{ kbps}$$
- **Impact on 100 kbps GFSK Physical Layer:**
  - Audio frame duration: $128 \text{ samples} / 16,000 \text{ Hz} = 8.0 \text{ ms}$.
  - Compressed payload: $128 / 2 = 64 \text{ bytes}$.
  - Packet overhead: Preamble (4 B) + Sync Word (2 B) + Header (8 B) + Payload (64 B) + CRC-16 (2 B) = 80 bytes (640 bits).
  - Transmission time:
    $$T_{\text{tx}} = \frac{640 \text{ bits}}{100,000 \text{ bps}} = 6.40 \text{ ms}$$
  - Channel duty cycle: $6.40 \text{ ms} / 8.00 \text{ ms} = 80.0\%$.
  - Required RX return window: 0.50 ms (6.25%).
  - Radio TX/RX switching turnaround: 0.20 ms (2.5%).
  - Total occupied channel time: $6.40 + 0.50 + 0.20 = 7.10 \text{ ms} / 8.00 \text{ ms} = 88.75\%$.
  - **Remaining timing margin: only 0.90 ms (11.25%)!**
  - This violates the required $\ge 20\%$ margin target. Any crystal drift or retransmission causes immediate audio buffer overflow.

---

### 5. RF Front-End & Antenna Audit
1. **Wrong Antenna Part & Footprint:**
   - The BOM and footprint used `Johanson_2450AT43F0100` (designed for 2.45 GHz WiFi/BLE, not 868 MHz Sub-GHz).
   - The correct 868 MHz component is **Johanson `0868AT43A0020E`**.
2. **Improper Antenna Pin Grounding:**
   - In Rev 1 PCB, Pin 2 of the antenna footprint was routed to `GND`.
   - The Johanson `0868AT43A0020E` datasheet explicitly specifies:
     - **Pin 1:** Feed (RF input)
     - **Pin 2:** NC (No Connect / mechanical anchoring pad only; MUST NOT connect to GND).
   - Grounding Pin 2 shorts or severely detunes the ceramic dielectric resonator.
3. **Matching Topology & Test Path:**
   - The ST AN5407/AN5457 reference matching network requires verified series/shunt inductor and capacitor values tuned for the high-power PA (+14 dBm).
   - No population-selectable conducted RF test path was provided (e.g. `R_ANT` / `R_TEST` pads for SMA/U.FL pigtail verification).

---

### Baseline Audit Conclusion
All 9 critical findings reported by the independent review are verified by direct tool execution and inspection. Rev 1 cannot be fabricated or brought up in its current state.
A complete in-place engineering repair plan is detailed in the accompanying `implementation_plan.md`.
