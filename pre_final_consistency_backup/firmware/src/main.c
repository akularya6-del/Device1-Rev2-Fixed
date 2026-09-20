/**
 * @file main.c
 * @brief Device 1 Main Application Loop
 * 
 * Hardware:
 * - MCU: STM32WL55CCU6 (Dual-Core ARM Cortex-M4 @ 48MHz)
 * - Microphone: Knowles SPH0645LM4H-B (I2S, 16kHz, 16-bit)
 * - Radio: Sub-GHz transceiver (868MHz, 2-GFSK, 100kbps, +14dBm)
 * - Power: 1S LiPo + AP2112K-3.3 LDO + MCP73831 Charger
 * - UI: Bi-Color Red/Blue LED
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "../include/hardware_config.h"
#include "../codec/adpcm.h"
#include "../audio/audio_i2s.h"
#include "../radio/subghz_radio.h"
#include "../power/power_mgr.h"
#include "../ui/led_ui.h"

/* Static Buffers & Codec State */
static adpcm_state_t s_adpcm_encoder;
static uint8_t s_compressed_payload[AUDIO_FRAME_BYTES_ADPCM];
static uint8_t s_packet_sequence = 0;

/* System Status */
static power_status_t s_power_status;

static void system_clock_config(void)
{
    /* 1. Set Flash latency to 2 Wait States for 48 MHz operation in Range 1 */
    FLASH->ACR = FLASH_ACR_LATENCY_2WS;

    /* 2. Configure Power scaling to Range 1 (1.2V) */
    PWR->CR1 |= PWR_CR1_VOS_RANGE1;

    /* 3. Enable HSE (32.0 MHz external crystal) */
    RCC->CR |= RCC_CR_HSEON;
    uint32_t timeout = 100000;
    while (!(RCC->CR & RCC_CR_HSERDY) && --timeout) {}

    if (timeout > 0) {
        /* HSE is stable: Configure PLL
         * HSE = 32 MHz
         * PLLM = /2 -> 16 MHz
         * PLLN = *6 -> 96 MHz VCO
         * PLLR = /2 -> 48 MHz SYSCLK (PLLREN = 1)
         */
        RCC->PLLCFGR = RCC_PLLCFGR_PLLSRC_HSE |
                       RCC_PLLCFGR_PLLM_DIV2  |
                       (6UL << 8)             | /* PLLN = 6 */
                       RCC_PLLCFGR_PLLREN     |
                       RCC_PLLCFGR_PLLR_DIV2;

        /* Enable PLL */
        RCC->CR |= RCC_CR_PLLON;
        timeout = 100000;
        while (!(RCC->CR & RCC_CR_PLLRDY) && --timeout) {}

        if (timeout > 0) {
            /* Switch SYSCLK to PLL */
            RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW_PLL) | RCC_CFGR_SW_PLL;
            timeout = 100000;
            while (((RCC->CFGR & RCC_CFGR_SWS_PLL) != RCC_CFGR_SWS_PLL) && --timeout) {}
        }
    }
}


int main(void)
{
    /* 1. Configure System Clocks and Buses */
    system_clock_config();

    /* 2. Initialize Peripherals */
    led_ui_init();
    power_mgr_init();
    audio_i2s_init();
    adpcm_reset(&s_adpcm_encoder);

    /* 3. Initialize Sub-GHz Radio (868MHz GFSK) */
    if (!subghz_radio_init()) {
        /* Radio init failure -> Flash Red Error pattern */
        led_ui_set_red(true);
        while (1) {}
    }

    /* 4. Start Audio Capture */
    audio_i2s_start();

    /* 5. Heartbeat Blue LED Flash on Successful Boot */
    led_ui_indicate_cmd(CMD_OPTION_A);

    /* Main Real-Time Audio Streaming Loop */
    while (1) {
        int16_t *pcm_frame = NULL;
        audio_buffer_id_t buf_id = audio_i2s_get_frame(&pcm_frame);

        if (buf_id != BUFFER_NONE && pcm_frame != NULL) {
            /* Record current predictor state before encoding for packet sync */
            int16_t frame_valprev = s_adpcm_encoder.valprev;
            int8_t  frame_index   = s_adpcm_encoder.index;

            /* Compress 128 samples (256 bytes) into 64 bytes */
            size_t bytes_encoded = adpcm_encode(&s_adpcm_encoder, pcm_frame, AUDIO_FRAME_SAMPLES, s_compressed_payload);

            if (bytes_encoded == AUDIO_FRAME_BYTES_ADPCM) {
                /* Transmit over-the-air at 868MHz 2-GFSK */
                subghz_radio_send_frame(s_packet_sequence++, frame_valprev, frame_index, s_compressed_payload);

                /* Quick 500us RX listening window for return ACK / Command */
                uint8_t received_cmd = CMD_ACK_NONE;
                if (subghz_radio_receive_ack(&received_cmd, 500)) {
                    if (received_cmd >= CMD_OPTION_A && received_cmd <= CMD_OPTION_D) {
                        /* Trigger visual feedback: A=1, B=2, C=3, D=4 flashes */
                        led_ui_indicate_cmd(received_cmd);
                    }
                }
            }
        }

        /* Periodic Housekeeping (called every ~8ms frame cycle) */
        led_ui_tick(8);
        
        /* Battery Monitoring */
        power_mgr_update(&s_power_status);
        if (s_power_status.level == BATTERY_CRITICAL) {
            /* Low-battery protection shutdown */
            audio_i2s_stop();
            subghz_radio_sleep();
            led_ui_set_red(true);
            power_mgr_sleep(5000);
            led_ui_set_red(false);
            power_mgr_sleep(60000);
        }
    }

    return 0;
}
