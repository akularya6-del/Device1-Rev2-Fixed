/**
 * @file hardware_config.h
 * @brief Hardware Pinout and System Configuration for Device 1
 * Open Architecture Compact Wireless Audio Terminal (Strictly Non-TI)
 * Target MCU: STM32WL55CCU6 (Dual-core ARM Cortex-M4 @ 48MHz)
 */

#ifndef HARDWARE_CONFIG_H
#define HARDWARE_CONFIG_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32wl55xx.h"

/* ====================================================================
 * Clock & Timing Definitions
 * ==================================================================== */
#define HSE_VALUE               32000000U       /* 32.0 MHz Murata XRCGB32M000F1H00R0 */
#define SYSCLK_FREQ             48000000U       /* 48.0 MHz Core Clock */
#define AUDIO_SAMPLE_RATE       16000U          /* 16.0 kHz Audio Sample Rate */
#define AUDIO_FRAME_SAMPLES     128U            /* 128 samples = 8.0 ms frame */
#define AUDIO_FRAME_BYTES_PCM   (AUDIO_FRAME_SAMPLES * 2U) /* 256 bytes 16-bit PCM */
#define AUDIO_FRAME_BYTES_ADPCM (AUDIO_FRAME_SAMPLES / 2U) /* 64 bytes 4-bit ADPCM */

/* ====================================================================
 * Sub-GHz RF Parameters (ETSI EN 300 220 European 868MHz Band)
 * ==================================================================== */
#define RF_FREQUENCY_HZ         868000000U      /* 868.0 MHz Carrier */
#define RF_BITRATE_BPS          150000U         /* 150 kbps 2-GFSK (44.2% timing margin) */
#define RF_FREQ_DEV_HZ          37500U          /* +/- 37.5 kHz FSK Deviation (h=0.5) */
#define RF_MOD_SHAPING_BT       0.5f            /* Gaussian filter BT=0.5 */
#define RF_TX_POWER_DBM         14              /* +14 dBm (High-Power RFO_HP) */
#define RF_SYNC_WORD_0          0x2D            /* Sync Word Byte 0 */
#define RF_SYNC_WORD_1          0xD4            /* Sync Word Byte 1 */
#define RF_PREAMBLE_BITS        32U             /* 32-bit Preamble */

/* ====================================================================
 * Packet Header Protocol
 * ==================================================================== */
#define PACKET_MAGIC            0x5741          /* 'WA' (Wireless Audio) */
#define PACKET_TYPE_AUDIO       0x01            /* Audio Streaming Packet */
#define PACKET_TYPE_ACK         0x02            /* Base Station ACK/Cmd Packet */

/* Return Command Codes (Base Station to Device 1) */
#define CMD_ACK_NONE            0x00
#define CMD_OPTION_A            0x41            /* 'A' */
#define CMD_OPTION_B            0x42            /* 'B' */
#define CMD_OPTION_C            0x43            /* 'C' */
#define CMD_OPTION_D            0x44            /* 'D' */

/* ====================================================================
 * GPIO Pin Assignments (Matches validation/MCU_PIN_AUDIT.csv)
 * ==================================================================== */
/* I2S2 Audio Interface (Knowles SPH0645) */
#define I2S2_WS_PORT            GPIOB
#define I2S2_WS_PIN             12              /* Pin 32: PB12 (AF5 I2S2_WS) */
#define I2S2_SCK_PORT           GPIOA
#define I2S2_SCK_PIN            9               /* Pin 17: PA9  (AF5 I2S2_CK) */
#define I2S2_SD_PORT            GPIOA
#define I2S2_SD_PIN             10              /* Pin 33: PA10 (AF5 I2S2_SD) */

/* UI Indicators (Bi-Color Red/Blue LED) */
#define LED_R_PORT              GPIOA
#define LED_R_PIN               4               /* Pin 12: PA4 (Red LED) */
#define LED_B_PORT              GPIOA
#define LED_B_PIN               5               /* Pin 13: PA5 (Blue LED) */

/* Power & Charging Management */
#define CHG_STAT_PORT           GPIOA
#define CHG_STAT_PIN            0               /* Pin 7:  PA0 (MCP73831 STAT) */

/* SWD Debug & Programming */
#define SWDIO_PORT              GPIOA
#define SWDIO_PIN               13              /* Pin 36: PA13 (AF0 SWDIO) */
#define SWCLK_PORT              GPIOA
#define SWCLK_PIN               14              /* Pin 42: PA14 (AF0 SWCLK) */

#endif /* HARDWARE_CONFIG_H */
