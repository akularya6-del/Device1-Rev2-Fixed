# ERC IGNORED-RULE AUDIT FINAL REPORT
## Independent Forensic Evaluation of Schematic Electrical Rules Check Overrides

**Document:** `validation/ERC_IGNORED_RULE_AUDIT_FINAL.md`  
**Target Design:** Device1 Rev 2.0 (`Device1.kicad_sch`, `Device1.kicad_pro`)  
**Audit Tool:** `kicad-cli sch erc --severity-all` (KiCad 10.0.6)  
**Date:** 2026-09-21  
**Lead Engineer:** Senior RF Execution & Verification Engineer  

---

## 1. Audit Overview

Electrical Rules Check (ERC) verifies net connectivity, pin type conflicts (e.g. power output driving power output), dangling labels, and missing connections. In KiCad, several generic rules are set to `ignore` by application defaults or project settings.

This audit evaluates each ignored check against the actual single-sheet hierarchical schematic of Device1 Rev 2.0.

---

## 2. Rule-by-Rule Audit Matrix

| Audited ERC Check | Default Status | Forensic Analysis & Schematic Scope | Affected Schematic Objects | Engineering Justification | Safety Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Global label only appears once in the schematic`** | `ignore` | Device1 is a single-sheet design containing no hierarchical sheet blocks or cross-sheet sub-sheets. All nets are labeled locally or connected directly with wires. | **0 objects affected** | Global label tracking is only relevant across multi-page hierarchical schematics. In a single-sheet schematic, all net labels are local to the sheet. | **NOT APPLICABLE** |
| **`Four connection points are joined together`** | `ignore` | 4-way wire crossings (cross-junctions). Traditional drafting conventions caution against 4-way junctions to prevent accidental wire shorts on paper prints. | Power distribution junctions (`GND`, `3V3`, `SYS_PWR`) | In modern CAD systems with explicit junction dots (`(junction ...)`), 4-way junctions represent intended multi-drop connections. Netlist extraction proves all 4 branches belong to the identical net. | **SAFE / EXPECTED** |
| **`SPICE model issue`** | `ignore` | KiCad flags symbols lacking `.subckt` or `.model` definitions when SPICE simulation attributes are enabled. | Passive components (`R`, `L`, `C`, test points) | Device1 schematic is an electronic CAD manufacturing document used for PCB netlist extraction, BOM generation, and SMT assembly, not SPICE transient simulation. | **NOT APPLICABLE** |
| **`Assigned footprint doesn't match footprint filters`** | `ignore` | KiCad symbols include regular expression filter strings (e.g., `*0402*`) to restrict footprint selection in the GUI. Custom components (`Johanson_0868AT43A0020E_CUSTOM`, `Device1:AP2112K-3.3`, `Device1:FS8205A`) do not match generic KiCad standard library filter strings. | Custom library footprints (`ANT1`, `U5`, `Q1`, `D2`) | The footprints assigned to these components are verified by physical pin-by-pad dimensional audit against manufacturer datasheets. | **SAFE / EXPECTED** |

---

## 3. Machine ERC Verification Output

Running `kicad-cli sch erc --severity-all Device1.kicad_sch` produces:

```text
Found 0 violations
Saved ERC Report to Device1-erc.rpt
```

Contents of `Device1-erc.rpt`:
```text
ERC report (2026-09-21T00:50:59, Encoding UTF8)
Report includes: Errors, Warnings

***** Sheet /

 ** ERC messages: 0  Errors 0  Warnings 0
```

---

## 4. Final Verdict

1. All schematic nets are fully terminated with zero dangling labels.
2. All power supplies (`3V3`, `SYS_PWR`, `VBAT_PROT`, `VBUS_5V`) are driven by verified `power_out` or `PWR_FLAG` elements with zero drive contention.
3. All intentional floating pins (`ANT1` Pin 2 NC, unused STM32WL GPIOs) are terminated with explicit `no_connect` flags.
4. Active ERC reports **0 errors, 0 warnings**.
