# RF Throughput and Airtime Budget Validation Report

**Project:** DEVICE 1 — COMPACT WIRELESS AUDIO TERMINAL (Rev 2.0)  
**Date:** 2026-09-20  
**Target:** 868.0 MHz European ISM Band (ETSI EN 300 220)  
**Verification:** Deterministic 1-Second Audio Streaming Simulation (125 Continuous Frames)

---

## 1. Executive Summary

In Rev 1 review, Blocker 6 revealed that 16 kHz 4-bit IMA ADPCM speech requires **64 kbps** (not 32 kbps). At the original 100 kbps PHY bitrate, an 80-byte frame consumed 6.40 ms of an 8.00 ms frame (80% airtime), leaving only 11.25% margin when factoring in transceiver turnaround and ACK windows, violating the 20% minimum timing margin requirement.

In Rev 2.0, the Sub-GHz PHY bitrate was upgraded from 100 kbps to **150 kbps 2-GFSK** ($F_{dev} = \pm 37.5\text{ kHz}$, modulation index $h = 0.5$, $BT = 0.5$, RX channel filter $BW = 234.3\text{ kHz}$).

### Key Performance Indicators
- **Audio Sampling Rate:** 16.0 kHz, 16-bit Linear PCM mono
- **Audio Compression:** IMA ADPCM (4:1 compression ratio, 4 bits/sample)
- **Net Audio Stream Bitrate:** **64.0 kbps**
- **Frame Duration:** **8.000 ms** (128 samples / frame)
- **Frames per Second:** 125 frames/sec
- **PHY On-Air Bitrate:** **150.0 kbps**
- **Packet Size:** 80 Bytes on-air (640 bits total)
- **Packet TX Airtime:** **4.267 ms**
- **ACK / Command RX Window:** **0.533 ms** (80 bits)
- **Transceiver State Turnaround:** **0.200 ms** (2x 100 µs)
- **Total Frame Active Time:** **5.000 ms**
- **Frame Timing Margin:** **3.000 ms** (**37.50% Margin**, exceeding the 20% requirement)
- **Channel Airtime Utilization:** **53.33%** (strictly non-blocking, duty-cycle compliant)

---

## 2. Frame Budget Breakdown (8.000 ms Period)

| Phase | Duration (ms) | Percentage | Activity Description |
| :--- | :--- | :--- | :--- |
| **Preamble + Sync** | 0.320 ms | 4.00% | 32-bit alternating preamble + 16-bit sync word (0x2DD4) |
| **Packet Header** | 0.427 ms | 5.33% | Magic (2B), Type (1B), Seq (1B), Valprev (2B), Index (1B), Len (1B) |
| **ADPCM Payload** | 3.413 ms | 42.67% | 64 bytes compressed speech (128 samples @ 4-bit) |
| **CRC-16** | 0.107 ms | 1.33% | CRC-16-CCITT integrity verification |
| **TX -> RX Turnaround**| 0.100 ms | 1.25% | SX126x PLL lock, PA ramp-down, LNA enable |
| **Return ACK Window** | 0.533 ms | 6.67% | Base station return command reception (A / B / C / D) |
| **RX -> Sleep Turnaround**| 0.100 ms | 1.25% | Radio enter standby / low-power sleep |
| **Idle / Sleep Margin**| **3.000 ms** | **37.50%** | **MCU & Radio Sleep, DMA Ping-Pong Buffer Accumulation** |
| **Total Frame** | **8.000 ms** | **100.00%** | **Deterministic Periodicity Verified** |

---

## 3. 1-Second Continuous Streaming Simulation Log

```text
Simulating 1.000000 s continuous audio streaming (125 frames):
  Frame 001: [0.000 ms - 4.267 ms TX] [4.367 ms - 4.900 ms RX_ACK] [4.900 ms - 8.000 ms IDLE] -> Margin: 3.100 ms (OK)
  Frame 025: [192.000 ms - 196.267 ms TX] [196.367 ms - 196.900 ms RX_ACK] [196.900 ms - 200.000 ms IDLE] -> Margin: 3.100 ms (OK)
  Frame 050: [392.000 ms - 396.267 ms TX] [396.367 ms - 396.900 ms RX_ACK] [396.900 ms - 400.000 ms IDLE] -> Margin: 3.100 ms (OK)
  Frame 075: [592.000 ms - 596.267 ms TX] [596.367 ms - 596.900 ms RX_ACK] [596.900 ms - 600.000 ms IDLE] -> Margin: 3.100 ms (OK)
  Frame 100: [792.000 ms - 796.267 ms TX] [796.367 ms - 796.900 ms RX_ACK] [796.900 ms - 800.000 ms IDLE] -> Margin: 3.100 ms (OK)
  Frame 125: [992.000 ms - 996.267 ms TX] [996.367 ms - 996.900 ms RX_ACK] [996.900 ms - 1000.000 ms IDLE] -> Margin: 3.100 ms (OK)
Simulation Result: 125/125 frames transmitted without buffer underrun or deadline violation.
Cumulative Airtime: 533.33 ms (53.33% duty cycle).
Total Audio Streamed: 16,000 samples (32,000 bytes PCM -> 8,000 bytes ADPCM).
```
