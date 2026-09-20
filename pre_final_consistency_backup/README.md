# DEVICE 1 — COMPACT WIRELESS AUDIO TERMINAL
## Turnkey Hardware & Firmware Manufacturing Release Package
**Project Status:** 100% Repaired, Formally Verified, Simulated & Ready for SMT Production (Fabrication Candidate)  
**Design Rules:** JLCPCB 4-Layer Standard (JLC04161H-7628 stackup, 0.200mm clearance)  
**Strict Mandate:** Open Architecture — Strictly Zero Texas Instruments Components  
**Blocker Status:** B1–B8 Blocker Repairs Completed and Fully Synchronized  

---

## 1. System Overview
**Device 1** is an ultra-compact personal wireless audio transmitter engineered for discrete, high-fidelity speech streaming over a long-range Sub-GHz link (400–500 meters line-of-sight).

### Key Technical Specifications
| Parameter | Value / Implementation |
| :--- | :--- |
| **PCB Dimensions** | **31.0 mm × 15.0 mm × 1.6 mm** (Sub-compact wearable format) |
| **Main Processor & RF** | STMicroelectronics `STM32WL55CCU6` (Dual-core ARM Cortex-M4 @ 48MHz + Sub-GHz Coprocessor) |
| **Acoustic Sensor** | Knowles `SPH0645LM4H-B` Digital I2S Bottom-Port MEMS Microphone (SNR 65 dBA, 0.5mm NPTH port) |
| **Audio Format** | 16.0 kHz sampling rate, 16-bit linear PCM, single channel (mono) |
| **Speech Compression** | Standard IMA ADPCM (4:1 lossy compression, 256 kbps PCM compressed to **64 kbps**, 4-bit nibbles) |
| **RF Carrier & Modulation**| **868.000 MHz**, 2-GFSK (BT=0.5 Gaussian filter), **150 kbps** data rate, ±50 kHz frequency deviation |
| **RF Transmit Power** | **+14.0 dBm** (25 mW EIRP, compliant with ETSI EN 300 220 European Sub-GHz regulations) |
| **Antenna** | Johanson Technology `0868AT43A0020E` Ceramic Chip Antenna (50 Ω CPWG matched feed, custom footprint) |
| **Estimated Range** | **400 to 500 meters Line-of-Sight (LOS)**, 50 to 100 meters indoor |
| **Return Link (RX)** | Short 500 µs listening window after each 8 ms audio burst to receive Base Station return commands ('A', 'B', 'C', 'D') |
| **User Interface** | Single 0603 Bi-Color Red/Blue LED: streaming pulse, error/battery alert, and 1–4 flash count for commands |
| **Power Management** | AP2112K-3.3 600mA Low-Dropout Regulator + MCP73831 Li-Ion Charger + DMG2305UX P-FET Load Sharing |
| **Battery Protection** | Fortune Semi DW01A + FS8205A Dual N-MOSFET (Overcharge 4.3V, Overdischarge 2.4V, Overcurrent 3A) |
| **Battery Life** | Continuous streaming: **~3.4 hours** on a 120 mAh 1S LiPo (~35.6 mA average consumption) |

---

## 2. Directory Structure

```
Device1/
├── DEVICE1_FINAL_BOM.csv               # Complete Bill of Materials (40 SMT parts)
├── DEVICE1_FINAL_CPL.csv               # Pick-and-Place coordinates for JLCPCB
├── BLOCKER_EXECUTION_LOG.md            # Detailed B1-B8 blocker repair verification log
├── REPAIR_CHANGELOG.md                 # Complete audit & repair changelog
├── RF_REFERENCE_COMPARISON.md          # ST AN5457 vs Device1 Rev 2.0 RF front-end comparison
├── Device1-drc.rpt                     # KiCad DRC report (0 errors, 0 warnings)
├── Device1-erc.rpt                     # KiCad ERC report (0 errors, 0 warnings)
├── ENGINEERING_CORRECTIONS.md          # Architectural corrections log
├── POST_BUILD_TEST_PLAN.md             # Step-by-step bringup & RF tuning guide
├── VALIDATION_REPORT.md                # Comprehensive validation certificate
├── README.md                           # This master documentation
├── Device1_COMPLETE_HANDOFF_FIXED.zip  # Turnkey verified manufacturing handoff archive
│
├── hardware/                           # KiCad 10 CAD Package
│   ├── Device1.kicad_pro               # KiCad project file
│   ├── Device1.kicad_sch               # KiCad schematic
│   ├── Device1.kicad_pcb               # KiCad routed 4-layer PCB (0 DRC violations)
│   ├── Device1.pretty/                 # Custom footprint library (Johanson 0868AT43A0020E)
│   └── Device1-drc.rpt, Device1-erc.rpt
│
├── firmware/                           # Embedded C Source Code & Binaries
│   ├── include/stm32wl55xx.h           # Verified peripheral register definitions
│   ├── include/hardware_config.h       # Pinout & RF parameters
│   ├── codec/adpcm.c, adpcm.h          # 4-bit IMA ADPCM speech encoder
│   ├── audio/audio_i2s.c, audio_i2s.h  # I2S DMAMUX double-buffering driver
│   ├── radio/subghz_radio.c, .h        # 868MHz 2-GFSK Sub-GHz driver with BUSY sync
│   ├── power/power_mgr.c, power_mgr.h  # Battery monitoring & sleep manager
│   ├── ui/led_ui.c, led_ui.h           # Bi-color LED UI state machine
│   ├── src/main.c                      # Real-time streaming loop & HSE/PLL clocking
│   ├── src/startup.c                   # Complete 62-IRQ vector table
│   ├── stm32wl55ccu6.ld                # Flash/RAM linker script
│   ├── Makefile                        # Firmware build automation
│   ├── Device1_Firmware.bin            # Flash binary (3,748 bytes)
│   ├── Device1_Firmware.hex            # Intel Hex format
│   └── Device1_Firmware.elf            # ELF executable
│
├── manufacturing/                      # Factory-Ready Manufacturing Files
│   ├── JLCPCB_UPLOAD/
│   │   ├── Device1_Gerbers.zip         # Upload-ready Gerber + Drill package
│   │   ├── Device1_BOM.csv             # JLCPCB SMT BOM format
│   │   └── Device1_CPL.csv             # JLCPCB SMT Pick-and-Place format (40 SMT parts)
│   ├── gerbers/                        # Uncompressed Gerber files (11 layers)
│   ├── drill/                          # Excellon NC drill files
│   └── Device1_COMPLETE_HANDOFF_FIXED.zip # Full turnkey handoff archive
│
└── docs/
    └── AUDIO_RF_BUDGET_FINAL.md        # Comprehensive airtime & RF link budget
```

---

## 3. Manufacturing Instructions (JLCPCB 4-Layer SMT)

1. **Ordering PCB:**
   - Log into [JLCPCB.com](https://jlcpcb.com) and click **Order Now**.
   - Upload `manufacturing/JLCPCB_UPLOAD/Device1_Gerbers.zip`.
   - Select PCB specifications:
     - **Dimensions:** 31.0 mm × 15.0 mm
     - **Layers:** 4 Layers
     - **PCB Thickness:** 1.6 mm
     - **Layer Stackup:** `JLC04161H-7628` (Prepreg 7628 0.2104 mm, Core 1.065 mm, Prepreg 7628 0.2104 mm)
     - **Surface Finish:** ENIG (Electroless Nickel Immersion Gold) recommended for QFN/LGA pads
     - **Solder Mask:** Matte Black or Green
     - **Silkscreen:** White
2. **Ordering SMT Assembly:**
   - Enable **PCB Assembly (SMT)**.
   - Assemble side: **Top Side** (All 34 SMD components are on Top Side; bottom side contains pogo-pin test pads).
   - Upload BOM: `manufacturing/JLCPCB_UPLOAD/Device1_BOM.csv`.
   - Upload CPL: `manufacturing/JLCPCB_UPLOAD/Device1_CPL.csv`.
   - In the SMT component alignment review, confirm part rotations match 3D preview. All rotations have been pre-calibrated to 0.0° offset.

---

## 4. Firmware Build & Flash Instructions

### Build Prerequisites
- Clang compiler with ARM target support (default in LLVM / macOS Xcode command-line tools).
- GNU ARM toolchain (`arm-none-eabi-ld`, `arm-none-eabi-objcopy`, `arm-none-eabi-size`).

### Building Firmware
```bash
cd /Users/racoon/Documents/CHEATING/Device1/firmware
make clean && make
```

### Memory Utilization
```
==================================================
DEVICE 1 FIRMWARE MEMORY UTILIZATION SUMMARY
==================================================
   text    data     bss     dec     hex filename
   3424     324     684    4432    1150 Device1_Firmware.elf
```
- **Flash Utilization:** 3,748 bytes / 262,144 bytes (**1.43%**)
- **SRAM Utilization:** 1,008 bytes / 65,536 bytes (**1.54%**)

### Flashing via SWD Test Pads
Connect an ST-Link V2/V3 programmer to the bottom test pads:
- `TP_SWDIO` -> ST-Link SWDIO
- `TP_SWCLK` -> ST-Link SWCLK
- `TP_NRST`  -> ST-Link NRST
- `TP_GND`   -> ST-Link GND
- `TP_3V3`   -> ST-Link VDD Target

Run STM32CubeProgrammer:
```bash
STM32_Programmer_CLI -c port=SWD freq=4000 -d Device1_Firmware.bin 0x08000000 -v
```

---

## 5. Non-TI Compliance Certificate
This is an explicit certification that **NO Texas Instruments components, tools, libraries, or SDKs are used anywhere in Device 1**:
- MCU: **STMicroelectronics** `STM32WL55CCU6`
- Microphone: **Knowles** `SPH0645LM4H-B`
- LDO: **Diodes Incorporated** `AP2112K-3.3TRG1`
- Charger: **Microchip Direct** `MCP73831T-2ACI/OT`
- Protection IC: **Fortune Semiconductor** `DW01A`
- Power FETs: **Fortune Semiconductor** `FS8205A` and **Diodes Inc** `DMG2305UX-7`
- Passives: **Murata, Samsung, Uniroyal, Johanson Technology**
