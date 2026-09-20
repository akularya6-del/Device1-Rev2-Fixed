/**
 * @file audio_i2s.h
 * @brief I2S Audio Acquisition Driver with Circular DMA Double-Buffering
 * Knowles SPH0645LM4H-B Digital I2S MEMS Microphone
 */

#ifndef AUDIO_I2S_H
#define AUDIO_I2S_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "../include/hardware_config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BUFFER_NONE = 0,
    BUFFER_PING = 1,
    BUFFER_PONG = 2
} audio_buffer_id_t;

/**
 * @brief Initialize I2S2 peripheral and DMA1 Channel for microphone sampling
 * Configures 16 kHz, 16-bit mono, circular double-buffering.
 */
void audio_i2s_init(void);

/**
 * @brief Start continuous I2S DMA capture
 */
void audio_i2s_start(void);

/**
 * @brief Stop I2S DMA capture
 */
void audio_i2s_stop(void);

/**
 * @brief Check if a double-buffer frame is ready for compression
 * @param frame_out Pointer to receive pointer to the 128-sample PCM frame
 * @return audio_buffer_id_t Identifier of the ready buffer (BUFFER_NONE if not ready)
 */
audio_buffer_id_t audio_i2s_get_frame(int16_t **frame_out);

/**
 * @brief DMA Half-Transfer complete interrupt callback (called by ISR)
 */
void audio_i2s_dma_half_transfer_callback(void);

/**
 * @brief DMA Transfer complete interrupt callback (called by ISR)
 */
void audio_i2s_dma_transfer_callback(void);

#ifdef __cplusplus
}
#endif

#endif /* AUDIO_I2S_H */
