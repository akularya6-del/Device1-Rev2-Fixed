# PACKET SERIALIZATION & WIRE LAYOUT FINAL REPORT
## Verification of Memory Packing, Byte Offsets, and Deterministic Wire Serialization

**Document:** `validation/PACKET_LAYOUT_FINAL.md`  
**Target Architecture:** STM32WL55CCU6 (ARM Cortex-M4 @ 48 MHz)  
**Radio Core:** Integrated Sub-GHz Transceiver (SX126x compatible)  
**Date:** 2026-09-21  
**Lead Engineer:** Senior RF Execution & Verification Engineer  
**Status:** **PASSED (Bit-Exact, Zero-Padding Packing Verified)**

---

## 1. Structure Definition & Packing Directives

In `firmware/radio/subghz_radio.h` lines 19–39:

```c
#pragma pack(push, 1)
typedef struct {
    uint16_t magic;         /**< PACKET_MAGIC (0x5741) */
    uint8_t  type;          /**< PACKET_TYPE_AUDIO or PACKET_TYPE_ACK */
    uint8_t  seq_num;       /**< Rolling sequence counter (0..255) */
    int16_t  valprev;       /**< IMA ADPCM predictor state for sync */
    int8_t   index;         /**< IMA ADPCM step index for sync */
    uint8_t  payload_len;   /**< Payload length (AUDIO_FRAME_BYTES_ADPCM = 64) */
} radio_header_t;

typedef struct {
    radio_header_t header;
    uint8_t payload[AUDIO_FRAME_BYTES_ADPCM];
} radio_audio_packet_t;

typedef struct {
    radio_header_t header;
    uint8_t cmd_code;       /**< CMD_OPTION_A, B, C, or D */
    uint8_t reserved[3];
} radio_ack_packet_t;
#pragma pack(pop)
```

The `#pragma pack(push, 1)` directive instructs the Clang compiler to pack all structure members without byte padding.

---

## 2. Machine-Verified Memory Offsets and Field Alignment

Host compilation with Clang/GCC verification confirms the following memory layout:

| Field | Type | Size (Bytes) | Byte Offset | Wire Endianness | Value / Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `header.magic` | `uint16_t` | 2 | `+0` | Little-Endian (`0x41`, `0x57`) | `0x5741` ('WA' Wireless Audio) |
| `header.type` | `uint8_t` | 1 | `+2` | Single Byte | `0x01` (`PACKET_TYPE_AUDIO`) |
| `header.seq_num` | `uint8_t` | 1 | `+3` | Single Byte | `0..255` rolling packet sequence |
| `header.valprev` | `int16_t` | 2 | `+4` | Little-Endian (LSB, MSB) | Predicted PCM sample state for decoder resync |
| `header.index` | `int8_t` | 1 | `+6` | Single Byte | Quantizer step table index (`0..88`) |
| `header.payload_len` | `uint8_t` | 1 | `+7` | Single Byte | `64` (Payload byte count) |
| `payload[0..63]` | `uint8_t[64]`| 64 | `+8 .. +71` | Sequential Nibble Pairs | 128 samples compressed as 4-bit IMA ADPCM |
| **Total Struct Size**| | **72 bytes** | | | **Zero internal padding, zero trailing padding** |

### Code Verification:
- `sizeof(radio_header_t)` $= \mathbf{8\text{ bytes}}$
- `sizeof(radio_audio_packet_t)` $= \mathbf{72\text{ bytes}}$
- `offsetof(radio_audio_packet_t, payload)` $= \mathbf{8\text{ bytes}}$

---

## 3. Over-the-Air (OTA) Physical Layer Framing

The STM32WL Sub-GHz radio core automatically encapsulates the 72-byte payload with hardware framing elements:

```
+---------------+----------------+---------------------------------+---------------+
| Preamble      | Sync Word      | Packed Audio Payload            | CRC-16        |
| (32 bits / 4B)| (16 bits / 2B) | (radio_audio_packet_t: 72 Bytes)| (16 bits / 2B)|
+---------------+----------------+---------------------------------+---------------+
```

| Framing Field | Size (Bytes) | Hardware Configuration Parameter | OTA Byte Sequence |
| :--- | :--- | :--- | :--- |
| **Preamble** | 4 | `RADIO_SET_PACKETPARAMS` (`0x00, 0x20`) | Alternating `0xAA, 0xAA, 0xAA, 0xAA` |
| **Sync Word** | 2 | `RADIO_WRITE_REGISTER` (`0x06C0`) | `0x2D, 0xD4` |
| **Radio Header** | 8 | From `s_tx_packet.header` | 8 bytes (Magic, Type, Seq, ADPCM State, Len) |
| **ADPCM Audio Data**| 64 | From `s_tx_packet.payload` | 64 bytes (128 packed 4-bit audio nibbles) |
| **CRC-CCITT** | 2 | `RADIO_SET_PACKETPARAMS` (`0x02` 2-byte CRC) | Hardware calculated 16-bit CRC polynomial |
| **Total OTA Packet** | **80 bytes** | **640 bits total** | Fully serialized deterministic bitstream |

---

## 4. Endianness and Serialization Integrity

1. **Deterministic Byte Stream:** The ARM Cortex-M4 core operates in Little-Endian mode. Transmitted multi-byte integers (`magic` and `valprev`) are placed in the radio TX FIFO directly via `subghz_write_buffer(0, (uint8_t*)&s_tx_packet, sizeof(radio_audio_packet_t))`.
2. **Reconstruction at Receiver:** The receiver reconstructs `valprev` as `(int16_t)(buf[4] | (buf[5] << 8))`, ensuring cross-platform interoperability without endianness ambiguity.
3. **Struct Padding Immunity:** Because all fields are explicitly typed fixed-width integers (`uint8_t`, `int8_t`, `uint16_t`, `int16_t`) and enclosed within `#pragma pack(push, 1)`, no compiler-dependent padding can occur on ARM or GCC/Clang targets.
