# Post-Build Hardware & Firmware Bringup Test Plan
## Device 1 — Compact Wireless Audio Terminal
**Revision:** 1.0  
**Target:** Prototype Bringup, Power-On Verification, RF Tuning, and Audio Streaming  

---

### 1. Equipment & Tools Required
1. **Power Supply & Metering:**
   - Adjustable DC Lab Power Supply (0–5.0V, current limit set to 50 mA initial, 200 mA active).
   - Digital Multimeter (6.5 digit DMM or standard handheld DMM) with needle probes.
   - USB Power Meter (measuring VBUS voltage and charge current).
2. **RF Test Equipment:**
   - Spectrum Analyzer or Software Defined Radio (SDR, e.g. RTL-SDR / HackRF / BladeRF) tuned to 868.0 MHz.
   - Vector Network Analyzer (NanoVNA or high-end VNA) calibrated 800 MHz – 1000 MHz.
   - 50-ohm RF pigtail with U.FL or semi-rigid probe soldered across `R_ANT` / `ANT1`.
3. **Debug & Programming:**
   - ST-Link V3 / V2 or J-Link ARM programmer.
   - Pogo-pin test jig or 0.1" breakout cable connecting to test points on B.Cu (`TP_SWDIO`, `TP_SWCLK`, `TP_NRST`, `TP_3V3`, `TP_GND`).
4. **Audio & Acoustic:**
   - Acoustic test chamber or quiet room with 1 kHz calibrated tone generator at 94 dBSPL.
   - Base station receiver / PC audio decoder running `firmware/tools/adpcm` decoder.

---

### 2. Step-by-Step Bringup Procedure

#### Step 1: Unpowered Inspection & Impedance Checks (Cold Board)
1. **Visual Inspection:**
   - Inspect under stereo microscope at 20x magnification.
   - Verify solder joint fillets on U1 (QFN-48), MK1 (LGA-6), and SOT-23 packages.
   - Verify acoustic hole under MK1 is 100% free of solder paste or conformal flux residue.
2. **Power Rail Resistance to Ground:**
   - Measure resistance between `3V3` and `GND`: Expected > 50 kΩ (Capacitors charging up). If < 100 Ω, DO NOT POWER ON (investigate shorted capacitor or bridge).
   - Measure resistance between `SYS_PWR` and `GND`: Expected > 50 kΩ.
   - Measure resistance between `VBAT_PROT` and `GND`: Expected > 100 kΩ.
   - Measure resistance between `VBUS_5V` and `GND`: Expected > 100 kΩ.

#### Step 2: Power-Path & Voltage Regulation Verification
1. **Bench Supply Power (Battery Input):**
   - Connect bench supply to `TP_BATT_P` (+) and `TP_BATT_N` (-).
   - Set supply to 3.70 V with 50 mA current limit.
   - Switch on bench supply.
   - Measure `SYS_PWR` voltage: Expected **3.65V – 3.70V** (DMG2305UX P-FET fully conducting).
   - Measure `3V3` voltage at AP2112K-3.3 output: Expected **3.30V ± 0.05V**.
   - Measure quiescent current: Expected **< 2 mA** in unprogrammed MCU state.
2. **USB Power & Load Sharing:**
   - Connect 5.00 V to `TP_VBUS` and `GND`.
   - Measure `SYS_PWR` voltage: Expected **4.65V – 4.75V** (VBUS supplying system through body diode / load sharing).
   - Verify DMG2305UX gate is pulled HIGH by VBUS, isolating the LiPo battery from supplying load current during charge.
   - Verify MCP73831 Pin 1 (`CHG_STAT`) pulls LOW, indicating charge mode active.

#### Step 3: SWD Programming & Core Clock Verification
1. **Debugger Connection:**
   - Connect ST-Link to `TP_SWDIO`, `TP_SWCLK`, `TP_NRST`, `TP_GND`.
   - Run `openocd -f interface/stlink.cfg -f target/stm32wlx.cfg` or STM32CubeProgrammer CLI:
     ```bash
     STM32_Programmer_CLI -c port=SWD freq=4000 -d Device1_Firmware.bin 0x08000000 -v
     ```
   - Verify Device ID detected: `0x497` (STM32WL55 Dual-Core).
   - Flash `Device1_Firmware.bin`.
2. **HSE 32MHz Clock Verification:**
   - Measure test clock or radio PLL lock flag.
   - Verify core boots successfully: Blue LED flashes once (`CMD_OPTION_A` heartbeat indicator).

#### Step 4: Digital Audio (I2S) Verification
1. **Clock Probing:**
   - Probe `MIC_SCK` (PA9): Verify 512.0 kHz square wave (3.3V CMOS levels).
   - Probe `MIC_WS` (PB12): Verify 16.00 kHz 50% duty cycle word select clock.
2. **Audio Data Capture:**
   - Expose the device to a 1 kHz reference tone at 94 dBSPL.
   - Probe `MIC_SD` (PA10): Verify 18-bit 2's complement audio words streaming in real time.
   - Check I2S DMA double-buffering: Verify DMA transfer-complete interrupts fire precisely every 8.0 ms.

#### Step 5: RF 868MHz 2-GFSK Transmitter & Modulation Tests
1. **Carrier Frequency & Spectral Purity:**
   - Position SDR / Spectrum Analyzer antenna near Device 1.
   - Verify RF burst occurs every 8.0 ms:
     - Center Frequency: **868.000 MHz ± 5 kHz**
     - Occupied Bandwidth (-20 dB): **< 200 kHz**
     - Output Power: **+14.0 dBm ± 1.5 dB** at antenna feedpoint
     - Harmonic Suppression: 2nd harmonic (1736 MHz) < -40 dBm, 3rd harmonic (2604 MHz) < -45 dBm (meeting ETSI EN 300 220 limits).
2. **Packet Transmission Integrity:**
   - Demodulate packets using base station SDR / receiver.
   - Verify Preamble (32 bits `0xAA`), Sync Word (`0x2D, 0xD4`), Header (`0x5741`), and sequence numbers incrementing without gaps.
   - Run IMA ADPCM decoder on 64-byte payload: Verify clear, intelligible reconstructed speech audio with SNR > 20 dB.

#### Step 6: Return Command Feedback & LED UI Tests
1. **Transceiver ACK Link:**
   - Send return command packet from Base Station during the 500 us RX window:
     - Send Command 'A': Verify Device 1 Blue LED emits **1 flash**.
     - Send Command 'B': Verify Device 1 Blue LED emits **2 flashes**.
     - Send Command 'C': Verify Device 1 Blue LED emits **3 flashes**.
     - Send Command 'D': Verify Device 1 Blue LED emits **4 flashes**.

#### Step 7: Battery Life & Low-Power Profiling
1. **Current Consumption Profile:**
   - Continuous 868MHz Audio Streaming:
     - I2S DMA active: ~3.5 mA
     - MCU Core (48 MHz): ~6.5 mA
     - RF Transmit (+14 dBm, 100 kbps, 6.4 ms / 8.0 ms burst): ~32 mA peak, **~25.6 mA average**
     - Total Average Operating Current: **~35.6 mA**
   - Battery Runtime on 120 mAh 1S LiPo:
     $$T = \frac{120 \text{ mAh}}{35.6 \text{ mA}} \approx 3.37 \text{ hours continuous streaming}$$
   - Sleep / Idle Mode: < 15 uA.
2. **Overdischarge Cutoff:**
   - Lower bench supply voltage below 3.20 V: Verify Red LED low-battery indicator flashes.
   - Lower bench supply below 2.40 V: Verify DW01A protection IC disconnects battery low-side via FS8205A MOSFETs, drawing zero current (< 100 nA).
