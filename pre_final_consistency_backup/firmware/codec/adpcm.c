/**
 * @file adpcm.c
 * @brief Implementation of standard IMA ADPCM 4-bit Speech Codec
 */

#include "adpcm.h"

/* Step size index quantization table (4 bits) */
static const int8_t indexTable[16] = {
    -1, -1, -1, -1, 2, 4, 6, 8,
    -1, -1, -1, -1, 2, 4, 6, 8
};

/* Step size table for 89 quantizer levels */
static const int16_t stepsizeTable[89] = {
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
    19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
    50, 55, 60, 66, 73, 80, 88, 97, 107, 118,
    130, 143, 157, 173, 190, 209, 230, 253, 279, 307,
    337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
    876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066,
    2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358,
    5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899,
    15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794, 32767
};

void adpcm_reset(adpcm_state_t *state) {
    if (state) {
        state->valprev = 0;
        state->index = 0;
    }
}

static inline uint8_t encode_sample(adpcm_state_t *state, int16_t val) {
    int32_t valprev = state->valprev;
    int32_t index = state->index;
    int32_t step = stepsizeTable[index];
    int32_t diff = val - valprev;
    uint8_t delta = 0;

    if (diff < 0) {
        delta = 8;
        diff = -diff;
    }

    int32_t vpdiff = step >> 3;

    if (diff >= step) {
        delta |= 4;
        diff -= step;
        vpdiff += step;
    }
    step >>= 1;
    if (diff >= step) {
        delta |= 2;
        diff -= step;
        vpdiff += step;
    }
    step >>= 1;
    if (diff >= step) {
        delta |= 1;
        vpdiff += step;
    }

    if (delta & 8) {
        valprev -= vpdiff;
    } else {
        valprev += vpdiff;
    }

    /* Clamp predictor */
    if (valprev > 32767) valprev = 32767;
    else if (valprev < -32768) valprev = -32768;

    /* Update index */
    index += indexTable[delta];
    if (index < 0) index = 0;
    else if (index > 88) index = 88;

    state->valprev = (int16_t)valprev;
    state->index = (int8_t)index;

    return delta;
}

static inline int16_t decode_sample(adpcm_state_t *state, uint8_t delta) {
    int32_t valprev = state->valprev;
    int32_t index = state->index;
    int32_t step = stepsizeTable[index];

    int32_t vpdiff = step >> 3;
    if (delta & 4) vpdiff += step;
    if (delta & 2) vpdiff += (step >> 1);
    if (delta & 1) vpdiff += (step >> 2);

    if (delta & 8) {
        valprev -= vpdiff;
    } else {
        valprev += vpdiff;
    }

    /* Clamp output */
    if (valprev > 32767) valprev = 32767;
    else if (valprev < -32768) valprev = -32768;

    /* Update index */
    index += indexTable[delta & 0x0F];
    if (index < 0) index = 0;
    else if (index > 88) index = 88;

    state->valprev = (int16_t)valprev;
    state->index = (int8_t)index;

    return (int16_t)valprev;
}

size_t adpcm_encode(adpcm_state_t *state, const int16_t *pcm_in, size_t num_samples, uint8_t *adpcm_out) {
    if (!state || !pcm_in || !adpcm_out || num_samples == 0) return 0;

    size_t out_bytes = 0;
    for (size_t i = 0; i < num_samples; i += 2) {
        uint8_t delta0 = encode_sample(state, pcm_in[i]);
        uint8_t delta1 = 0;
        if (i + 1 < num_samples) {
            delta1 = encode_sample(state, pcm_in[i + 1]);
        }
        /* Pack low nibble first, high nibble second */
        adpcm_out[out_bytes++] = (uint8_t)((delta1 << 4) | (delta0 & 0x0F));
    }
    return out_bytes;
}

size_t adpcm_decode(adpcm_state_t *state, const uint8_t *adpcm_in, size_t num_bytes, int16_t *pcm_out) {
    if (!state || !adpcm_in || !pcm_out || num_bytes == 0) return 0;

    size_t out_samples = 0;
    for (size_t i = 0; i < num_bytes; i++) {
        uint8_t byte = adpcm_in[i];
        uint8_t delta0 = byte & 0x0F;
        uint8_t delta1 = (byte >> 4) & 0x0F;

        pcm_out[out_samples++] = decode_sample(state, delta0);
        pcm_out[out_samples++] = decode_sample(state, delta1);
    }
    return out_samples;
}
