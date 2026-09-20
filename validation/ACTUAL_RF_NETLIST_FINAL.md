# ACTUAL RF NETLIST FINAL EXTRACTION REPORT
## Forensic Pad-by-Pad Verification of Device1 Rev 2.0 RF Front-End

**Document:** `validation/ACTUAL_RF_NETLIST_FINAL.md`  
**Extracted Sources:**  
- `Device1.kicad_sch` (Lines 4070–4220, 4800–5107)  
- `Device1.kicad_pcb` (Footprint & Pad Definitions, Lines 240–355, 637–765, 1081–1289, 1740–2020, 5070–5220, 6679–7350)  
- `DEVICE1_FINAL_BOM.csv` (Lines 2, 3, 12–19)  
**Extraction Date:** 2026-09-21  
**Engineer:** Senior RF Execution & Verification Engineer  

---

## 1. STM32WL55CCU6 (U1) Transceiver Pin Extraction

From `Device1.kicad_pcb` Footprint `U1` (`QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm`, Position $X = 7.50\,\text{mm}$, $Y = 13.00\,\text{mm}$, Rotation $180^\circ$):

| Pin # | Pin Name on Symbol | PCB Pad Relative $(X, Y)$ | PCB Absolute Coordinate | Net Assignment | Physical Connection / Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pin 20** | `RFI_P` | $(+0.75, +3.4375)$ rot $180^\circ$ | $(6.750, 9.5625)\,\text{mm}$ | `/RFI_P` | Differential LNA In-Phase Input to `L3.2` & `C22.2` |
| **Pin 21** | `RFI_N` | $(+1.25, +3.4375)$ rot $180^\circ$ | $(6.250, 9.5625)\,\text{mm}$ | `/RFI_N` | Differential LNA Quadrature Input to `L3.1` & `C23.1` |
| **Pin 22** | `RFO_LP` | $(+1.75, +3.4375)$ rot $180^\circ$ | $(5.750, 9.5625)\,\text{mm}$ | *(No Net / Unconnected)* | Low-Power PA Output (Unused, isolated, DNC) |
| **Pin 23** | `RFO_HP` | $(+2.25, +3.4375)$ rot $180^\circ$ | $(5.250, 9.5625)\,\text{mm}$ | `/RFO_HP` | High-Power PA Output (+14 dBm) to `L1.1`, `C13.1`, `L2.2` |
| **Pin 24** | `VR_PA` | $(+2.75, +3.4375)$ rot $180^\circ$ | $(4.750, 9.5625)\,\text{mm}$ | `/VR_PA` | PA Internal Power Supply from LDO/SMPS to `L2.1` & `C4` |
| **Pin 49** | `EP` (Exposed Pad) | $(0.00, 0.00)$ rot $180^\circ$ | $(7.500, 13.000)\,\text{mm}$ | `/GND` | RF Ground Return (Solid 3×3 via array to Layer 2 `In1_Cu`) |

---

## 2. RF Front-End Component Pad Extraction

### 2.1 Power Amplifier DC Feed (`L2`)
- **Reference:** `L2`
- **Value:** $47\,\text{nH}$ $\pm 5\%$ (Murata `LQG15HS47NJ02D`, 0402, LCSC `C1038`)
- **Footprint:** `Inductor_SMD:L_0402_1005Metric` at $(4.100, 8.250)\,\text{mm}$, rot $0^\circ$
  - **Pad 1:** smd roundrect at $(3.615, 8.250)\,\text{mm}$, Net `/VR_PA`. Connected to `VR_PA` bus and decoupled by `C4` (100 nF to GND).
  - **Pad 2:** smd roundrect at $(4.585, 8.250)\,\text{mm}$, Net `/RFO_HP`. Connected to `U1.23`, `C13.1`, and `L1.1`.

### 2.2 Transmit Matching & Low-Pass Filter (`C13`, `L1`, `C14`)
- **Reference:** `C13`
  - **Value:** $2.2\,\text{pF}$ 50V C0G (Murata `GJM1555C1H2R2CB01D`, 0402, LCSC `C39744`)
  - **Footprint:** `Capacitor_SMD:C_0402_1005Metric` at $(3.800, 6.800)\,\text{mm}$, rot $180^\circ$
  - **Pad 1:** at $(4.280, 6.800)\,\text{mm}$, Net `/RFO_HP`
  - **Pad 2:** at $(3.320, 6.800)\,\text{mm}$, Net `/GND`
  - **Role:** Shunt capacitor at PA output forming input pole of transmit matching network.
- **Reference:** `L1`
  - **Value:** $3.3\,\text{nH}$ $\pm 0.3\,\text{nH}$ (Murata `LQG15HS3N3S02D`, 0402, LCSC `C1033`)
  - **Footprint:** `Inductor_SMD:L_0402_1005Metric` at $(5.250, 6.800)\,\text{mm}$, rot $90^\circ$
  - **Pad 1:** at $(5.250, 7.285)\,\text{mm}$, Net `/RFO_HP`
  - **Pad 2:** at $(5.250, 6.315)\,\text{mm}$, Net `/RF_50OHM`
  - **Role:** Series inductor transforming PA impedance to $50\,\Omega$ and providing harmonic rejection.
- **Reference:** `C14`
  - **Value:** $1.5\,\text{pF}$ 50V C0G (Murata `GJM1555C1H1R5CB01D`, 0402, LCSC `C39743`)
  - **Footprint:** `Capacitor_SMD:C_0402_1005Metric` at $(3.800, 5.200)\,\text{mm}$, rot $180^\circ$
  - **Pad 1:** at $(4.280, 5.200)\,\text{mm}$, Net `/RF_50OHM`
  - **Pad 2:** at $(3.320, 5.200)\,\text{mm}$, Net `/GND`
  - **Role:** Shunt capacitor at $50\,\Omega$ node completing the 3rd-order Pi-network.

### 2.3 Receive Balun & Differential Matching (`C22`, `L3`, `C23`)
- **Reference:** `C22`
  - **Value:** $1.5\,\text{pF}$ 50V C0G (Murata `GJM1555C1H1R5CB01D`, 0402, LCSC `C39743`)
  - **Footprint:** `Capacitor_SMD:C_0402_1005Metric` at $(6.650, 6.150)\,\text{mm}$, rot $0^\circ$
  - **Pad 1:** at $(6.165, 6.150)\,\text{mm}$, Net `/RF_50OHM`
  - **Pad 2:** at $(7.135, 6.150)\,\text{mm}$, Net `/RFI_P`
  - **Role:** Series AC coupling capacitor feeding 50 $\Omega$ single-ended signal into balanced LNA input.
- **Reference:** `L3`
  - **Value:** $18\,\text{nH}$ $\pm 5\%$ (Murata `LQG15HS18NJ02D`, 0402, LCSC `C1035`)
  - **Footprint:** `Inductor_SMD:L_0402_1005Metric` at $(6.000, 8.380)\,\text{mm}$, rot $0^\circ$
  - **Pad 1:** at $(5.515, 8.380)\,\text{mm}$, Net `/RFI_N`
  - **Pad 2:** at $(6.485, 8.380)\,\text{mm}$, Net `/RFI_P`
  - **Role:** Differential shunt inductor forming resonant balun across differential LNA pins.
- **Reference:** `C23`
  - **Value:** $1.5\,\text{pF}$ 50V C0G (Murata `GJM1555C1H1R5CB01D`, 0402, LCSC `C39743`)
  - **Footprint:** `Capacitor_SMD:C_0402_1005Metric` at $(6.650, 7.100)\,\text{mm}$, rot $0^\circ$
  - **Pad 1:** at $(6.165, 7.100)\,\text{mm}$, Net `/RFI_N`
  - **Pad 2:** at $(7.135, 7.100)\,\text{mm}$, Net `/GND`
  - **Role:** Phase balance capacitor grounding the negative differential branch for balanced-to-unbalanced conversion.

### 2.4 Antenna Feed & Test Selection (`R_ANT`, `R_TEST`, `TP_RF`, `ANT1`)
- **Reference:** `R_ANT`
  - **Value:** $0\,\Omega$ jumper (Uniroyal `0402WGF0000TCE`, 0402, LCSC `C17168`, Populated)
  - **Footprint:** `Resistor_SMD:R_0402_1005Metric` at $(5.250, 4.800)\,\text{mm}$, rot $90^\circ$
  - **Pad 1:** at $(5.250, 5.310)\,\text{mm}$, Net `/RF_50OHM`
  - **Pad 2:** at $(5.250, 4.290)\,\text{mm}$, Net `/ANT_FEED`
- **Reference:** `R_TEST`
  - **Value:** $0\,\Omega$ jumper (Uniroyal `0402WGF0000TCE`, 0402, LCSC `C17168`, **DNP**)
  - **Footprint:** `Resistor_SMD:R_0402_1005Metric` at $(6.800, 5.200)\,\text{mm}$, rot $0^\circ$
  - **Pad 1:** at $(6.290, 5.200)\,\text{mm}$, Net `/RF_50OHM`
  - **Pad 2:** at $(7.310, 5.200)\,\text{mm}$, Net `/TP_RF`
- **Reference:** `TP_RF`
  - **Footprint:** `TestPoint:TestPoint_Pad_D1.0mm` at $(9.800, 7.200)\,\text{mm}$ on `B.Cu`
  - **Pad 1:** at $(9.800, 7.200)\,\text{mm}$, Net `/TP_RF`
- **Reference:** `ANT1`
  - **Value:** `0868AT43A0020E` (Johanson Technology, LCSC `C2897287`)
  - **Footprint:** `Device1:Johanson_0868AT43A0020E_CUSTOM` at $(7.500, 2.000)\,\text{mm}$, rot $0^\circ$
  - **Pad 1 (Feed):** at $(4.450, 2.000)\,\text{mm}$ ($X = 7.50 - 3.05$), Net `/ANT_FEED`
  - **Pad 2 (NC):** at $(10.550, 2.000)\,\text{mm}$ ($X = 7.50 + 3.05$), unconnected SMD pad (no electrical net)

---

## 3. Physical Signal Path Summary

1. **Transmit Path:**
   `U1.23 (RFO_HP)` $\to$ `L1 (3.3 nH series, bypassed by C13 2.2 pF)` $\to$ `Net /RF_50OHM (bypassed by C14 1.5 pF)` $\to$ `R_ANT (0R)` $\to$ `Net /ANT_FEED` $\to$ `ANT1.1 (Johanson Antenna Feed)`.
2. **Receive Path:**
   `ANT1.1` $\to$ `Net /ANT_FEED` $\to$ `R_ANT (0R)` $\to$ `Net /RF_50OHM` $\to$ `C22 (1.5 pF series)` $\to$ `Net /RFI_P` $\to$ `U1.20 (RFI_P)`, with balanced differential conversion through `L3 (18 nH)` to `Net /RFI_N` $\to$ `U1.21 (RFI_N)` and phase balance via `C23 (1.5 pF)` to `GND`.
3. **Common Node:**
   `Net /RF_50OHM` is the central single-ended $50\,\Omega$ node shared directly between the TX Pi-filter output, the RX balun input, the conducted test jumper `R_TEST`, and the antenna feed jumper `R_ANT`.

---

## 4. Verification Conclusion

The actual schematic and PCB have been extracted to the individual pad, trace, and coordinate level. The circuit physically matches the discrete 7-element network reported in `DEVICE1_FINAL_CONSISTENCY_REPAIR_PLAN.md`.
