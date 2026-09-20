/**
 * @file adpcm.h
 * @brief Reference IMA ADPCM 4-bit Speech Encoder / Decoder
 * 
 * Implements standard IMA ADPCM conforming to the Interactive Multimedia Association spec.
 * Provides exact 4:1 compression from 16-bit signed linear PCM to 4-bit nibbles.
 */

#ifndef ADPCM_H
#define ADPCM_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int16_t valprev; /**< Previous output value (-32768 to 32767) */
    int8_t  index;   /**< Current step size index (0 to 88) */
} adpcm_state_t;

/**
 * @brief Reset ADPCM state structure
 */
void adpcm_reset(adpcm_state_t *state);

/**
 * @brief Encode 16-bit linear PCM samples into 4-bit IMA ADPCM
 * @param state Pointer to persistent ADPCM state
 * @param pcm_in Pointer to array of 16-bit signed PCM samples
 * @param num_samples Number of 16-bit PCM input samples (must be even for packed bytes)
 * @param adpcm_out Pointer to output buffer for packed 4-bit nibbles (num_samples / 2 bytes)
 * @return Number of compressed bytes written to adpcm_out
 */
size_t adpcm_encode(adpcm_state_t *state, const int16_t *pcm_in, size_t num_samples, uint8_t *adpcm_out);

/**
 * @brief Decode 4-bit IMA ADPCM stream back into 16-bit linear PCM samples
 * @param state Pointer to persistent ADPCM state
 * @param adpcm_in Pointer to buffer of packed 4-bit ADPCM bytes
 * @param num_bytes Number of input compressed bytes
 * @param pcm_out Pointer to output buffer for 16-bit PCM samples (num_bytes * 2 samples)
 * @return Number of 16-bit PCM samples reconstructed
 */
size_t adpcm_decode(adpcm_state_t *state, const uint8_t *adpcm_in, size_t num_bytes, int16_t *pcm_out);

#ifdef __cplusplus
}
#endif

#endif /* ADPCM_H */
