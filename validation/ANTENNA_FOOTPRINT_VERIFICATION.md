# ANTENNA FOOTPRINT VERIFICATION

**Document:** `validation/ANTENNA_FOOTPRINT_VERIFICATION.md`  
**Target Part Number:** Johanson Technology `0868AT43A0020001E` (Legacy P/N: `0868AT43A0020`)  
**Footprint Name:** `Johanson_0868AT43A0020E_CUSTOM`  
**Primary Source:** Johanson Technology Datasheet Doc# 36S00210 Rev 2.0, Pages 2, 3, 5  
**Verification Date:** 2026-09-20  

---

## 1. Dimensional Comparison Table

| Parameter | Datasheet Specification | KiCad Custom Footprint | Discrepancy | Result |
|---|---|---|---|---|
| **Component Body Length ($L$)** | $7.00 \pm 0.20\text{ mm}$ | $7.00\text{ mm}$ (Fab Outline: $X = \pm 3.50\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Component Body Width ($W$)** | $2.00 \pm 0.20\text{ mm}$ | $2.00\text{ mm}$ (Fab Outline: $Y = \pm 1.00\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Component Height ($T$)** | $0.80\text{ mm}$ ($+0.10 / -0.20\text{ mm}$) | $0.80\text{ mm}$ (Nominal) | $0.00\text{ mm}$ | **PASS** |
| **Terminal Width ($a$)** | $0.50 \pm 0.30\text{ mm}$ | $0.50\text{ mm}$ (Component Metallization) | $0.00\text{ mm}$ | **PASS** |
| **Recommended Pad Length ($X$)** | $1.00\text{ mm}$ (Pages 3 & 5 dimension `1`) | $1.00\text{ mm}$ (Pad $X$-size: $1.00\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Recommended Pad Width ($Y$)** | $1.80\text{ mm}$ (Pages 3 & 5 dimension `1.8`) | $1.80\text{ mm}$ (Pad $Y$-size: $1.80\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Inner Pad Gap** | $5.10\text{ mm}$ (Pages 3 & 5 dimension `5.1`) | $5.10\text{ mm}$ (Pad edges at $\pm 2.55\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Center-to-Center Pad Spacing** | $6.10\text{ mm}$ ($5.10 + 1.00$) | $6.10\text{ mm}$ (Pads at $X = -3.05\text{ mm}, +3.05\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Outer Pad Span** | $7.10\text{ mm}$ (Pages 3 & 5 dimension `7.1`) | $7.10\text{ mm}$ (Outer pad edges at $\pm 3.55\text{ mm}$) | $0.00\text{ mm}$ | **PASS** |
| **Pad Corner Radius** | Standard SMT Roundrect ($r = 0.20$) | Roundrect ratio: $0.20$ | $0.00$ | **PASS** |
| **Courtyard Margin** | $\ge 0.25\text{ mm}$ past body/pads | $X = \pm 3.85\text{ mm}$, $Y = \pm 1.25\text{ mm}$ | $\ge 0.25\text{ mm}$ | **PASS** |
| **Pin 1 (Feed) Function** | Feed Terminal | Net: `/ANT_FEED` | Verified | **PASS** |
| **Pin 2 (NC) Function** | Mechanical Anchor Only (NC) | Unconnected Pad (No Net) | Verified | **PASS** |

---

## 2. Rejection of Defective 2.4 GHz Footprint

The previous design incorrectly used the footprint `Johanson_2450AT43F0100` from the standard KiCad library.

| Feature | Defective `Johanson_2450AT43F0100` | Target `Johanson_0868AT43A0020E` | Physical Consequence of Old Footprint |
|---|---|---|---|
| **Intended Frequency** | $2.4\text{ GHz} - 2.5\text{ GHz}$ | $868\text{ MHz}$ ($858-878\text{ MHz}$) | Incorrect resonance |
| **Body Dimensions** | $6.0 \times 2.0\text{ mm}$ | $7.0 \times 2.0\text{ mm}$ | 1.0 mm length discrepancy |
| **Pad Size** | $1.20 \times 2.20\text{ mm}$ | $1.00 \times 1.80\text{ mm}$ | Excessive solder volume, wrong fillet |
| **Center-to-Center** | $5.70\text{ mm}$ ($\pm 2.85\text{ mm}$) | $6.10\text{ mm}$ ($\pm 3.05\text{ mm}$) | Pads spaced 0.40 mm too narrow! |
| **Inner Gap** | $4.50\text{ mm}$ | $5.10\text{ mm}$ | Severe risk of terminal short / detuning |

**Result:** The 2.4 GHz footprint is physically incompatible with the 868 MHz component. Replacement with `Johanson_0868AT43A0020E_CUSTOM` is mandatory.

---

## 3. Ground Clearance and Keep-Out Zone Verification

- **Datasheet Rule:** Minimum clearance free of metal above and below the antenna.
- **Board Outline:** $15.0\text{ mm}$ wide $\times 31.0\text{ mm}$ long.
- **Antenna Position:** Centered at $X = 7.50\text{ mm}$, $Y = 2.00\text{ mm}$.
- **Body Extent:** $X = [4.00, 11.00]\text{ mm}$, $Y = [1.00, 3.00]\text{ mm}$.
- **PCB Copper Keepout:**
  - All copper zones (`F.Cu`, `In1.Cu`, `In2.Cu`, `B.Cu`) start at $Y = 4.30\text{ mm}$.
  - The region $Y = [0.00, 4.30]\text{ mm}$ across the entire $15.0\text{ mm}$ width is completely free of copper planes on all 4 layers.
  - Clearance below antenna body: $4.30 - 3.00 = 1.30\text{ mm}$ to top of ground plane.
  - Clearance to board top edge: $1.00\text{ mm}$.
  - Clearance to side edges: $4.00\text{ mm}$ on left and right.
- **Result:** **PASS**
