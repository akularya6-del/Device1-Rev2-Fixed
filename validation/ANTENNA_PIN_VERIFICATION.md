# ANTENNA PIN VERIFICATION

**Document:** `validation/ANTENNA_PIN_VERIFICATION.md`  
**Target Part Number:** Johanson Technology `0868AT43A0020001E` (Legacy P/N: `0868AT43A0020`)  
**Primary Source:** Johanson Technology Datasheet Doc# 36S00210, Rev 2.0, Page 2 ("Terminal Configuration")  
**Verification Date:** 2026-09-20  

---

## 1. Primary Source Evidence

From Johanson Technology Datasheet `0868AT43A0020001E` Page 2:

```
Terminal Configuration
-------------------------------------------------------------
Pin Number       Function
-------------------------------------------------------------
1                Feed
2                NC*
-------------------------------------------------------------
* This terminal must be soldered for anchoring and mechanical stability.
```

### Mechanical Diagram Terminal Orientation
- **Bottom View:**
  - Pin 1 is marked with a circled "1" and designated as the **Feed** terminal.
  - Pin 2 is marked with a circled "2" and designated as the **NC** (No Connect) anchor terminal.
- **Top / Side View:**
  - The antenna body is symmetric ceramic LTCC, but the orientation must place Pin 1 facing the matching network feedline (`/ANT_FEED`).

---

## 2. Hardware Implementation Rules

1. **Pin 1 (Feed):**
   - Must connect to the 50 Ω RF coplanar waveguide feedline net `/ANT_FEED`.
   - Connected to the output of the RF front-end matching network.
   - Status: **VERIFIED & CONNECTED**.

2. **Pin 2 (NC / Mechanical Anchor):**
   - Per datasheet footnote: *"This terminal must be soldered for anchoring and mechanical stability."*
   - It is an electrically isolated pad.
   - Per project engineering instructions: *"If pin 2 is NC: keep it electrically unconnected."*
   - Therefore, Pad 2 is an SMD copper pad on `F.Cu`, with solder mask opening (`F.Mask`) and solder paste (`F.Paste`), but with **NO NET assignment** (electrically floating/isolated from GND and all other signals).
   - Status: **VERIFIED & IMPLEMENTED AS UNCONNECTED SMD PAD**.

---

## 3. Comparison with Previous Defective Implementation

| Pin | Previous (Johanson_2450AT43F0100) | Current (Johanson_0868AT43A0020E_CUSTOM) | Status |
|---|---|---|---|
| Pin 1 | Feed (2.4 GHz footprint, 1.2 x 2.2 mm pad @ X=-2.85mm) | Feed (868 MHz footprint, 1.0 x 1.8 mm pad @ X=-3.05mm) | **CORRECTED** |
| Pin 2 | NC (2.4 GHz footprint, 1.2 x 2.2 mm pad @ X=+2.85mm) | NC (868 MHz footprint, 1.0 x 1.8 mm pad @ X=+3.05mm) | **CORRECTED** |

**Conclusion:** Antenna pin functions are 100% verified against primary manufacturer documentation.
