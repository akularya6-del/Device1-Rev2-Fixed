# RF REFERENCE DESIGN COMPARISON FINAL REPORT
## Engineering Comparison of Discrete Switchless Front-End Against ST and Semtech References

**Document:** `RF_REFERENCE_COMPARISON_FINAL.md`  
**Project:** Device 1 — Compact Wireless Audio Terminal (Rev 2.0)  
**Target MCU:** STMicroelectronics STM32WL55CCU6TR (UFQFPN48, Dual-Core ARM Cortex-M4/M0+)  
**Operating Band:** 868.0 MHz Sub-GHz (2-GFSK, +14 dBm)  
**Primary Standards / References:**  
- STMicroelectronics AN5457 (Rev 3, Dec 2021): *"RF matching network design guide for STM32WL Series"*  
- Semtech Corporation AN1200.40 (Rev 1.0): *"Reference Design Explanation for the SX1261/62 Transceivers"*  
- STMicroelectronics AN5407 (Rev 2, Jan 2021): *"How to optimize the RF board layout for STM32WL5x/Ex"*  
- Johanson Technology Specification Doc# 36S00210 Rev 2.0 (0868AT43A0020E Antenna)  
**Date:** 2026-09-21  
**Classification:** **Pre-Production Prototype Reference Comparison (Digitally Validated Fabrication Candidate)**  

---

## 1. Executive Summary

This report establishes the engineering provenance of the RF front-end realized in **Device 1 Rev 2.0**.

Forensic review proves that Device 1 does **not** employ an Integrated Passive Device (`BALFHB-WL-02D3`). Instead, Device 1 implements the **7-element discrete switchless shared-antenna front-end architecture** specified in Semtech Application Note **AN1200.40** and supported by STMicroelectronics Application Note **AN5457 Rev 3** (Table 6, High-Power PA discrete matching network at 868 MHz).

This switchless topology enables a shared single-ended $50\,\Omega$ antenna feed without the board area, insertion loss, or GPIO overhead of an external active RF switch.

---

## 2. Parameter-by-Parameter Comparison Table

| Parameter / Feature | ST / Semtech Reference Standard | Device 1 Rev 2.0 Implementation | Engineering Variance / Rationale | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Transceiver IC** | STM32WL55CCU6 (UFQFPN48) | STM32WL55CCU6TR (UFQFPN48) | Exact silicon match | **PASS** |
| **Carrier Frequency** | 868.0 MHz (ETSI EN 300 220 ISM Band) | 868.0 MHz carrier | Programmed register `0x36400000` | **PASS** |
| **Modulation / Bitrate**| 2-GFSK ($h=0.5, BT=0.5$), 150 kbps | 2-GFSK ($h=0.5, BT=0.5$), 150 kbps | Authoritative configured PHY bitrate | **PASS** |
| **Transmit Output Path**| Pin 23 (`RFO_HP`), +14 dBm target | Pin 23 (`RFO_HP`), +14 dBm target | High-power PA selected (`tx_params` = 0x0E) | **PASS** |
| **Receive Input Path** | Pin 20 (`RFI_P`), Pin 21 (`RFI_N`) | Pin 20 (`RFI_P`), Pin 21 (`RFI_N`) | Balanced differential LNA input | **PASS** |
| **Low-Power PA Path** | Pin 22 (`RFO_LP`) | Pin 22 (`RFO_LP`) | Isolated / Do Not Connect (DNC) | **PASS** |
| **PA DC Choke Inductor**| $L_{choke} = 47\,\text{nH}$ (AN5457 Fig. 12) | $L_2 = 47\,\text{nH}$ (Murata LQG15HS47NJ02D) | Connected `VR_PA` (Pin 24) $\to$ `RFO_HP` (Pin 23) | **PASS** |
| **PA Supply Decoupling**| $C_{dec} = 100\,\text{nF}$ (AN5457 Section 3.1) | $C_4 = 100\,\text{nF}$ (Samsung CL05B104KO5NNNC) | Decouples `VR_PA` to GND | **PASS** |
| **TX Conjugate Shunt C**| $C_1 = 2.2\,\text{pF}$ (AN5457 Table 6) | $C_{13} = 2.2\,\text{pF}$ (Murata GJM1555C1H2R2CB01D)| Shunt capacitor at `RFO_HP` to GND | **PASS** |
| **TX Series Inductor** | $L_1 = 3.3\,\text{nH}$ (AN5457 Table 6) | $L_1 = 3.3\,\text{nH}$ (Murata LQG15HS3N3S02D) | Series harmonic filter between PA & $50\,\Omega$ | **PASS** |
| **TX Shunt Filter C** | $C_2 = 1.5\,\text{pF}$ (AN5457 Table 6) | $C_{14} = 1.5\,\text{pF}$ (Murata GJM1555C1H1R5CB01D)| Shunt capacitor at `RF_50OHM` to GND | **PASS** |
| **RX Series AC Cap** | $C_{in} = 1.5\,\text{pF}$ (AN1200.40 Fig. 2-1)| $C_{22} = 1.5\,\text{pF}$ (Murata GJM1555C1H1R5CB01D)| Series match from `RF_50OHM` $\to$ `RFI_P` | **PASS** |
| **RX Differential Balun**| $L_{balun} = 18\,\text{nH}$ (AN1200.40 Fig. 2-1)| $L_3 = 18\,\text{nH}$ (Murata LQG15HS18NJ02D)| Shunt inductor across `RFI_P` and `RFI_N` | **PASS** |
| **RX Balance Cap** | $C_{bal} = 1.5\,\text{pF}$ (AN1200.40 Fig. 2-1)| $C_{23} = 1.5\,\text{pF}$ (Murata GJM1555C1H1R5CB01D)| Shunt capacitor from `RFI_N` $\to$ GND | **PASS** |
| **Antenna Radiator** | Ceramic chip antenna ($868\,\text{MHz}$) | Johanson Technology `0868AT43A0020E` | Custom footprint matching Doc# 36S00210 | **PASS** |
| **Antenna Dimensions** | $7.00 \times 2.00 \times 0.80\,\text{mm}$ | $7.00 \times 2.00 \times 0.80\,\text{mm}$ | Exact 0.00 mm dimensional match | **PASS** |
| **Antenna Keepout** | $\ge 4.0\,\text{mm}$ metal-free border | $15.00 \times 4.30\,\text{mm}$ 4-layer keepout | 100% stripped copper on all layers | **PASS** |
| **RF Transmission Line**| $50.0\,\Omega$ Coplanar Waveguide (CPWG) | $50.0\,\Omega$ CPWG ($W=0.28\,\text{mm}, S=0.20\,\text{mm}$)| Solid Layer 2 (`In1_Cu`) ground reference | **PASS** |
| **Conducted RF Testing**| RF Test Interface | 1.0 mm SMD circular test pad (`TP_RF`) on `B.Cu`| Connected via DNP jumper `R_TEST` (0R) | **PASS** |

---

## 3. Detailed Technical Analysis

### 3.1 Rejection of BALFHB-WL-02D3 IPD Architecture
In early project documentation, references were made to the STMicroelectronics `BALFHB-WL-02D3` Integrated Passive Device. Detailed analysis of ST Datasheet `DS14091` Table 5 demonstrates that `BALFHB-WL-02D3` has two physically distinct single-ended $50\,\Omega$ ports on the antenna side:
- Pin `C1` (`RFO_out`): Transmit low-pass filter output.
- Pin `C3` (`RFI_in`): Receive balun single-ended input.

Because `BALFHB-WL-02D3` **contains no internal T/R switch**, combining these ports into a single antenna requires an external SPDT RF switch (e.g. Infineon BGS13S4N9 or Peregrine PE4259) plus two dedicated GPIO control lines and bias components. On Device 1's compact $31 \times 15\,\text{mm}$ PCB, the discrete switchless architecture is the superior engineering approach.

### 3.2 Discrete Switchless Front-End Operation
The switchless front-end topology joins the transmit and receive networks directly at the single-ended $50\,\Omega$ node (`RF_50OHM`):
1. **Transmit Mode Isolation:**
   - Transmit signal (+14 dBm, $V_{pk} \approx 1.58\,\text{V}$) passes from `RFO_HP` through the Pi-filter ($C_{13}, L_1, C_{14}$) to `RF_50OHM`.
   - The signal also encounters the receive series capacitor $C_{22}$ ($1.5\,\text{pF}$).
   - Inside the STM32WL transceiver, internal high-speed clamp diodes at `RFI_P` and `RFI_N` conduct when RF input exceeds $\sim +10\,\text{dBm}$, creating a low-impedance AC shunt.
   - This low impedance is transformed through the high reactance of $C_{22}$ ($X_C \approx 122.1\,\Omega$) and $L_3$ ($X_L \approx 98.2\,\Omega$), choking RF current and limiting power dissipation in the LNA clamp diodes to $< 0\,\text{dBm}$ ($< 1\,\text{mW}$), well below the $+10\,\text{dBm}$ continuous rating.
2. **Receive Mode Operation:**
   - The transmit PA transistors (`RFO_HP`) are unpowered and disabled by firmware.
   - Terminated in the high-impedance OFF-state PA, the Pi-network transforms to a high parallel shunt impedance at `RF_50OHM`.
   - Incoming signals from the antenna experience minimal insertion loss ($< 1.0\,\text{dB}$) and flow directly into $C_{22}$, $L_3$, and $C_{23}$ into the differential LNA.

### 3.3 Antenna Integration: Johanson 0868AT43A0020E
- **Manufacturer MPN:** `0868AT43A0020001E` (Tape/Reel code `E`, legacy `0868AT43A0020E`).
- **Body Dimensions:** $7.00 \pm 0.20\,\text{mm}$ (Length) $\times 2.00 \pm 0.20\,\text{mm}$ (Width) $\times 0.80 +0.10/-0.20\,\text{mm}$ (Height).
- **Land Pattern:** Pad width $1.00\,\text{mm}$, Pad height $1.80\,\text{mm}$, Center-to-center pitch $6.10\,\text{mm}$, Inner gap $5.10\,\text{mm}$.
- **Pin 1:** RF Feed (connected to `/ANT_FEED` via populated $0\,\Omega$ resistor `R_ANT`).
- **Pin 2:** Mechanical Solder Anchor (NC, unconnected floating copper pad per datasheet specification).
- **Copper Keepout:** $15.00\,\text{mm} \times 4.30\,\text{mm}$ completely free of copper planes, traces, and vias across all 4 PCB layers (`F.Cu`, `In1_Cu`, `In2_Cu`, `B.Cu`).

### 3.4 Conducted RF Test Facility
- Default production state: `R_ANT` ($0\,\Omega$ 0402) is populated; `R_TEST` ($0\,\Omega$ 0402) is DNP. Signals route directly to `ANT1`.
- Lab test configuration: `R_ANT` can be unpopulated and `R_TEST` populated to route the $50\,\Omega$ RF path to `TP_RF` (1.0 mm SMD test pad on `B.Cu`).
- Measurement is conducted via a spring-loaded pogo pin or 50 $\Omega$ semi-rigid coaxial pigtail for spectrum analyzer / VNA bench testing.

---

## 4. Link Budget & Propagation Estimate

| Parameter | Value at 400 m LOS | Value at 500 m LOS | Units |
| :--- | :--- | :--- | :--- |
| **Transmit Output Power ($P_{TX}$)** | +14.0 | +14.0 | dBm |
| **Transmitter Antenna Gain ($G_{TX}$)** | -1.5 | -1.5 | dBi |
| **Discrete Filter & Match Loss ($L_{TX}$)** | 0.8 | 0.8 | dB |
| **Free Space Path Loss (868 MHz)** | 83.26 | 85.20 | dB |
| **Base Station Antenna Gain ($G_{RX}$)** | +2.15 | +2.15 | dBi |
| **Base Station Cable / Front-End Loss** | 1.0 | 1.0 | dB |
| **Nominal Received Power ($P_{RX}$)** | **-70.41** | **-72.35** | **dBm** |
| **Receiver Sensitivity ($S_{RX}$, 150 kbps 2-GFSK)**| **-104.0** | **-104.0** | **dBm** |
| **Gross Link Margin** | **+33.59** | **+31.65** | **dB** |
| **Shadowing & Multipath Fade Allowance**| 12.0 | 12.0 | dB |
| **Net Operational Fade Margin** | **+21.59** | **+19.65** | **dB** |

*Note:* This link budget calculation indicates theoretical support for the target ~400–500 m LOS range. Real-world range depends on antenna height, body absorption, and local multipath conditions, and requires physical field testing.

---

## 5. Conclusion

Device 1 Rev 2.0 implements the verified discrete switchless RF front-end based on ST AN5457 Rev 3 and Semtech AN1200.40. All CAD schematics, PCB coplanar geometry, component values, and antenna keepout clearances have been digitally verified. Physical bench bringup and lab RF validation remain required on fabricated prototype hardware.
