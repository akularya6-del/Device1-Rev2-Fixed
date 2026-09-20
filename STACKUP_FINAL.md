# FINAL PCB STACKUP SPECIFICATION

**Document:** `STACKUP_FINAL.md`  
**Project:** Device1 Rev 2.0  
**Manufacturer / Process:** JLCPCB Standard 4-Layer Controlled Impedance  
**Stackup Code:** `JLC04161H-7628`  
**Verification Date:** 2026-09-20  

---

## 1. Physical Layer Stackup Details

| Layer Name | Type | Material | Nominal Thickness | Dielectric Constant ($\epsilon_r$) | Copper Weight / Notes |
|---|---|---|---|---|---|
| **Top Solder Mask** | Dielectric | Taiyo PSR-4000 (or equiv) | $0.015\text{ mm}$ | $3.8$ | Color: Green / Matte Black |
| **Layer 1: F.Cu** | Signal / Component | Copper Foil | $0.035\text{ mm}$ ($1.4\text{ mil}$) | — | 1 oz finished copper |
| **Dielectric 1-2** | Prepreg | FR-4 7628 | $0.2104\text{ mm}$ ($8.28\text{ mil}$) | $4.34$ (@ 868 MHz) | Glass fiber / resin composite |
| **Layer 2: In1.Cu** | Plane | Copper (Internal) | $0.0175\text{ mm}$ ($0.7\text{ mil}$) | — | 0.5 oz solid GND reference |
| **Dielectric 2-3** | Core | FR-4 Core | $1.0650\text{ mm}$ ($41.93\text{ mil}$) | $4.50$ | Rigid core substrate |
| **Layer 3: In2.Cu** | Plane / Route | Copper (Internal) | $0.0175\text{ mm}$ ($0.7\text{ mil}$) | — | 0.5 oz Power (`+3V3`, `VBAT`) |
| **Dielectric 3-4** | Prepreg | FR-4 7628 | $0.2104\text{ mm}$ ($8.28\text{ mil}$) | $4.34$ (@ 868 MHz) | Glass fiber / resin composite |
| **Layer 4: B.Cu** | Signal / Bottom | Copper Foil | $0.035\text{ mm}$ ($1.4\text{ mil}$) | — | 1 oz finished copper |
| **Bottom Solder Mask** | Dielectric | Taiyo PSR-4000 | $0.015\text{ mm}$ | $3.8$ | Color: Green / Matte Black |

### Overall Board Thickness
$$\text{Total Thickness} = 2 \times 0.015 + 2 \times 0.035 + 2 \times 0.0175 + 2 \times 0.2104 + 1.0650 \approx 1.60\text{ mm} \pm 10\%$$

---

## 2. RF Routing Constraints

1. **Unbroken Reference Plane:**
   - Layer 2 (`In1.Cu`) acts as the dedicated, unbroken solid ground reference plane directly beneath the RF front-end and coplanar feedline.
   - Zero plane splits, voids, or routing traces exist on Layer 2 under the RF path.
2. **Antenna Keepout Zone:**
   - Across the entire width ($X = [0.0, 15.0]\text{ mm}$) and top length ($Y = [0.0, 4.30]\text{ mm}$), all 4 copper layers (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`) are completely clear of copper fills, tracks, and pads (except for the antenna landing pads themselves).
   - This provides $1.30\text{ mm}$ of clear space between the bottom edge of the ceramic antenna and the start of the internal ground plane, strictly respecting Johanson Technology evaluation board guidelines.
