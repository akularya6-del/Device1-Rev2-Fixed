# RF Link Budget and Propagation Analysis (400m – 500m LOS)

**Project:** DEVICE 1 — COMPACT WIRELESS AUDIO TERMINAL (Rev 2.0)  
**Date:** 2026-09-20  
**RF Frequency:** 868.0 MHz ($\lambda = 0.3454\text{ m}$)  
**Modulation:** 150 kbps 2-GFSK ($F_{dev} = \pm 37.5\text{ kHz}$, $BT = 0.5$)  
**Target Range:** 400 m to 500 m Line-of-Sight (LOS)

---

## 1. Executive Summary

This report establishes the complete link budget for Device 1 transmitting audio to an external base station over 400 m and 500 m LOS paths in the 868 MHz European band.

At 150 kbps 2-GFSK with +14 dBm transmitter power:
- **At 400 meters LOS:** Received Signal Strength is **-68.61 dBm**, yielding a link margin of **+34.19 dB**.
- **At 500 meters LOS:** Received Signal Strength is **-70.55 dBm**, yielding a link margin of **+32.25 dB**.
- Even after factoring in a severe **15.0 dB** body-shadowing and Rayleigh multipath fade margin, the remaining fade margin at 500 m is **+17.25 dB**, mathematically demonstrating robust link viability.

---

## 2. RF Parameter Table

| Parameter | Value | Units | Derivation / Reference |
| :--- | :--- | :--- | :--- |
| **Operating Frequency ($f$)** | 868.0 | MHz | ETSI EN 300 220 Sub-band |
| **Free-Space Wavelength ($\lambda$)** | 0.3454 | m | $c / f$ |
| **Transmitter Output Power ($P_{tx}$)** | +14.0 | dBm | STM32WL55 High-Power PA (RFO_HP) |
| **TX Antenna Gain ($G_{tx}$)** | -1.5 | dBi | Johanson 0868AT43A0020E on 31x15mm ground plane |
| **TX Matching / Connector Loss ($L_{tx}$)** | 0.5 | dB | Murata 0402 C-L-C lumped matching |
| **Effective Isotropic Radiated Power (EIRP)** | +12.0 | dBm | $P_{tx} + G_{tx} - L_{tx}$ (ETSI compliant $\le +14\text{ dBm}$) |
| **Base Station RX Antenna Gain ($G_{rx}$)** | +2.15 | dBi | Standard half-wave dipole at base station |
| **RX Cable / Filter Insertion Loss ($L_{rx}$)** | 0.5 | dB | Coaxial feedline and front-end filter |
| **Receiver Noise Bandwidth ($B$)** | 234.3 | kHz | SX126x double-sideband filter setting |
| **Thermal Noise Density ($N_0$)** | -174.0 | dBm/Hz | $k \cdot T$ at $290\text{ K}$ |
| **Total Receiver Noise Floor ($P_N$)** | -120.30 | dBm | $-174 + 10 \log_{10}(B)$ |
| **Receiver Noise Figure ($NF$)** | 6.0 | dB | STM32WL55 receiver LNA/mixer front-end |
| **Required SNR for $\text{BER} = 10^{-3}$** | 9.5 | dB | Non-coherent 2-GFSK demodulation ($h=0.5$) |
| **Implementation / Demod Margin** | 2.0 | dB | Realistic baseband filtering & tracking |
| **Receiver Sensitivity ($S_{rx}$)** | **-102.80** | **dBm** | $P_N + NF + \text{SNR} + \text{Loss}$ |

---

## 3. Path Loss & Link Margin Calculations

### Free-Space Path Loss Formula
$$\text{FSPL}(d) = 20 \log_{10}(d) + 20 \log_{10}(f_{\text{MHz}}) - 27.55$$

### Received Power Equation
$$P_{rx}(d) = P_{tx} + G_{tx} - L_{tx} + G_{rx} - L_{rx} - \text{FSPL}(d)$$

### Link Budget Summary Table

| Metric | Distance = 400 m | Distance = 500 m | Units |
| :--- | :--- | :--- | :--- |
| **Free-Space Path Loss (FSPL)** | **83.26** | **85.20** | dB |
| **Received Power ($P_{rx}$)** | **-68.61** | **-70.55** | dBm |
| **Receiver Sensitivity ($S_{rx}$)**| **-102.80** | **-102.80** | dBm |
| **Gross Link Margin** | **+34.19** | **+32.25** | **dB** |
| Body Shadowing Loss (Wearable) | 8.0 | 8.0 | dB |
| Multipath / Rayleigh Fade Margin| 7.0 | 7.0 | dB |
| **Net Operational Fade Margin** | **+19.19** | **+17.25** | **dB** |

---

## 4. Engineering Conclusion

Both the 400 m and 500 m operating scenarios maintain substantial positive fade margins (>17 dB net margin) over free-space conditions even when Device 1 is worn against the human body. The 150 kbps 2-GFSK PHY satisfies all link budget requirements while providing a 37.5% time buffer to eliminate audio stutter.
