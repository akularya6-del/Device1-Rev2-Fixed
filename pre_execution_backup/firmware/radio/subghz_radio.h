/**
 * @file subghz_radio.h
 * @brief Sub-GHz 868MHz 2-GFSK Radio Driver for STM32WL55
 * Operates at 868.0 MHz, 100 kbps, 2-GFSK, +14 dBm output power.
 */

#ifndef SUBGHZ_RADIO_H
#define SUBGHZ_RADIO_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "../include/hardware_config.h"

#ifdef __cplusplus
extern "C" {
#endif

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

/**
 * @brief Initialize the Sub-GHz radio peripheral
 * Configures 868 MHz carrier, 100 kbps GFSK, +14 dBm PA, sync word and CRC.
 */
bool subghz_radio_init(void);

/**
 * @brief Transmit an ADPCM audio frame over the air
 * @param seq Sequence number
 * @param valprev ADPCM predictor value for this frame
 * @param index ADPCM step index for this frame
 * @param adpcm_data Pointer to 64 bytes of ADPCM compressed data
 * @return bool True if transmission initiated successfully
 */
bool subghz_radio_send_frame(uint8_t seq, int16_t valprev, int8_t index, const uint8_t *adpcm_data);

/**
 * @brief Listen for an ACK/Command response from the base station
 * @param cmd_received Pointer to receive command code ('A', 'B', 'C', 'D')
 * @param timeout_us Timeout in microseconds
 * @return bool True if a valid ACK packet was received
 */
bool subghz_radio_receive_ack(uint8_t *cmd_received, uint32_t timeout_us);

/**
 * @brief Put the radio into ultra-low-power standby/sleep mode
 */
void subghz_radio_sleep(void);

#ifdef __cplusplus
}
#endif

#endif /* SUBGHZ_RADIO_H */
