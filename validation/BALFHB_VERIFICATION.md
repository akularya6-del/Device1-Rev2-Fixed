# BALFHB-WL-02D3 VERIFICATION REPORT & DECISION GATE

**Document:** `validation/BALFHB_VERIFICATION.md`  
**Target Component:** STMicroelectronics `BALFHB-WL-02D3` (IPD Balun + Harmonic Filter)  
**Primary Source:** STMicroelectronics Datasheet `DS14091` Rev 2 (Dec 2022) & ST Reference Design `STDES-WL5U4IHH` / `MB1848`  
**Evaluation Date:** 2026-09-20  

---

## 1. Specification Verification Matrix

| Parameter | Specification in DS14091 | Target Device1 Rev 2 Requirement | Status |
|---|---|---|---|
| **Frequency Range** | 862 MHz to 928 MHz | 868.0 MHz (ETSI Band) | **VERIFIED** |
| **Supported Package** | STM32WL in UFQFPN48 package | STM32WL55CCU6 (UFQFPN48) | **VERIFIED** |
| **PCB Stackup** | Dedicated to 4-layer PCB | 4-layer PCB (JLC04161H-7628) | **VERIFIED** |
| **TX Matching Path** | Conjugate match to `RFO_HP` (+22 dBm max) | High-power PA `RFO_HP` (+14 dBm) | **VERIFIED** |
| **RX Balun Path** | Differential to 50 Ω single-ended (`RFI_P`, `RFI_N`) | Receiver input `RFI_P` (pin 20) & `RFI_N` (pin 21) | **VERIFIED** |
| **Harmonic Rejection** | Integrated deep Tx rejection harmonic filter | ETSI EN 300 220 2nd/3rd harmonics | **VERIFIED** |
| **Antenna Impedance** | 50 Ω nominal | 50 Ω nominal | **VERIFIED** |
| **Package** | CSPG 8 bumps, $2.13 \times 1.83\text{ mm}$, 0.4 mm pitch | SMD Assembly | **VERIFIED** |
| **LCSC Sourcing** | Part # C5350082, in stock (93 pcs) | Standard SMT | **VERIFIED** |

---

## 2. Critical Architecture Finding: Antenna-Port Separation

A detailed inspection of **DS14091 Table 5 ("Pads description top view")** reveals a crucial architectural constraint that was overlooked in previous planning documents:

```
Pad Ref    Pad Name       Description
------------------------------------------------------------------------
A1         RFO_in         Tx filter input (from STM32WL RFO_HP pin 23)
A2         RFI_N_out      Differential-N Rx balun output (to pin 21)
A3         RFI_P_out      Differential-P Rx balun output (to pin 20)
B1         GND2           Ground #2
B2         GND3           Ground #3
C1         RFO_out        Tx filter output (50 Ω single-ended)
C2         GND1           Ground #1
C3         RFI_in         Single-ended Rx balun input (50 Ω single-ended)
```

### Technical Assessment:
1. **No Internal T/R Switch:** The `BALFHB-WL-02D3` **DOES NOT** integrate a transmit/receive switch. It provides two separate 50 Ω single-ended ports on the antenna side:
   - `C1` (`RFO_out`): Transmit harmonic filter output.
   - `C3` (`RFI_in`): Receive balun input.
2. **ST Reference Design Implementation:** In ST's official reference boards (**MB1848** and **STDES-WL5U4IHH**), an external SP3T / SPDT RF switch (specifically the Infineon **BGS13S4N9** or Peregrine **PE4259**) is placed between `RFO_out`, `RFI_in`, and the antenna.
3. **Impossibility of Direct Tying:** Tying `C1` directly to `C3` without an active RF switch causes severe degradation:
   - When transmitting (+14 dBm = 25 mW), the transmit energy flows directly into the sensitive LNA input `C3`, violating maximum LNA input ratings and loading the PA output.
   - When receiving, the incoming microvolt RF signal is loaded and attenuated by the un-switched PA output impedance.
4. **DC PA Biasing:** `BALFHB-WL-02D3` is an IPD built on a non-conductive glass substrate. It does **not** provide DC bias to the internal PA. An external RF choke inductor from `VR_PA` (pin 24) to `RFO_HP` (pin 23) is still strictly required.

---

## 3. Decision Gate & Selection

Per Section 8 instructions:
> *"If any critical pin or network cannot be verified: DO NOT USE THE PART. Fall back to verified discrete reference design."*

Adding an external RF switch (BGS13S4N9 in 1.1 x 1.1 mm TSNP-9 package with 2 MCU GPIO control lines) plus the 0.4mm pitch CSP-8 BALFHB-WL-02D3 onto a dense 30 x 15 mm board would require extensive re-routing of digital control lines, whereas the verified ST discrete RF architecture (AN5457 / AN1200 / Semtech switchless reference) provides a direct, highly manufacturable solution using 0402 discrete components already established on the BOM.

### Architectural Choice:
We implement the **verified ST / Semtech 868 MHz discrete RF front-end architecture**:
1. **PA Biasing:** High-Q RF choke ($33\text{ nH}$ / $47\text{ nH}$) connecting `VR_PA` (pin 24) to `RFO_HP` (pin 23) with $100\text{ nF} + 47\text{ pF}$ decoupling.
2. **TX Matching & Low-Pass Filtering:** Series matching inductor and shunt capacitors forming a conjugate match from the PA output to 50 Ω, with harmonic rejection.
3. **RX Balun & Protection:** Balanced-to-unbalanced network connecting differential `RFI_P` (pin 20) and `RFI_N` (pin 21) to the 50 Ω node.
4. **DC Blocking & Antenna Tuning:** DC blocking capacitor leading to the Pi-tuning network (`L1`, `C13`, `C14`) and antenna feed `ANT1`.
