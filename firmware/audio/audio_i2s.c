/**
 * @file audio_i2s.c
 * @brief Real I2S Audio Acquisition Driver Implementation for STM32WL55
 * Implements circular DMA double buffering (ping-pong) for Knowles SPH0645 MEMS mic.
 */

#include "audio_i2s.h"
#include "hardware_config.h"
#include "stm32wl55xx.h"

/* DMA Circular Double Buffer: 256 samples total (Ping: 0..127, Pong: 128..255) */
#define TOTAL_DMA_SAMPLES   (AUDIO_FRAME_SAMPLES * 2U)

static int16_t s_dma_audio_buffer[TOTAL_DMA_SAMPLES];
static volatile audio_buffer_id_t s_ready_buffer = BUFFER_NONE;
static volatile bool s_is_running = false;

void audio_i2s_init(void)
{
    /* Clear buffers */
    for (size_t i = 0; i < TOTAL_DMA_SAMPLES; i++) {
        s_dma_audio_buffer[i] = 0;
    }
    s_ready_buffer = BUFFER_NONE;
    s_is_running = false;

    /* 1. Enable RCC Peripheral Clocks */
    RCC->AHB2ENR |= (RCC_AHB2ENR_GPIOAEN | RCC_AHB2ENR_GPIOBEN);
    RCC->AHB1ENR |= (RCC_AHB1ENR_DMA1EN | RCC_AHB1ENR_DMAMUX1EN);
    RCC->APB1ENR1 |= RCC_APB1ENR1_SPI2EN;

    /* Configure DMAMUX1 Channel 0 mapping to SPI2_RX request */
    DMAMUX1_Channel0->CCR = DMAMUX_REQ_SPI2_RX;

    /* 2. Configure GPIO Pins for AF5 (SPI2/I2S2) */
    /* PA9 (I2S2_CK): Pin 17, AF5 */
    GPIOA->MODER &= ~(3UL << (9 * 2));
    GPIOA->MODER |=  (2UL << (9 * 2));  /* Alternate Function */
    GPIOA->AFR[1] &= ~(0xFUL << ((9 - 8) * 4));
    GPIOA->AFR[1] |=  (5UL << ((9 - 8) * 4)); /* AF5 */
    GPIOA->OSPEEDR |= (3UL << (9 * 2)); /* Very High Speed */

    /* PA10 (I2S2_SD): Pin 33, AF5 */
    GPIOA->MODER &= ~(3UL << (10 * 2));
    GPIOA->MODER |=  (2UL << (10 * 2));
    GPIOA->AFR[1] &= ~(0xFUL << ((10 - 8) * 4));
    GPIOA->AFR[1] |=  (5UL << ((10 - 8) * 4)); /* AF5 */

    /* PB12 (I2S2_WS): Pin 32, AF5 */
    GPIOB->MODER &= ~(3UL << (12 * 2));
    GPIOB->MODER |=  (2UL << (12 * 2));
    GPIOB->AFR[1] &= ~(0xFUL << ((12 - 8) * 4));
    GPIOB->AFR[1] |=  (5UL << ((12 - 8) * 4)); /* AF5 */
    GPIOB->OSPEEDR |= (3UL << (12 * 2));

    /* 3. Configure I2S2 Peripheral in Master Receive Mode */
    SPI2->I2SCFGR = 0; /* Reset */
    /* Philips Standard, Master Receive, 16-bit extended in 32-bit frame */
    SPI2->I2SCFGR = SPI_I2SCFGR_I2SMOD | SPI_I2SCFGR_I2SCFG_MRX | SPI_I2SCFGR_I2SSTD_PH | SPI_I2SCFGR_CHLEN_32;

    /* Prescaler for 16.0 kHz Fs from 48MHz SYSCLK:
     * Bitclock = 16000 * 64 = 1.024 MHz
     * Prescaler divider: (48000000 / (2 * 1024000)) = 23.43 -> I2SDIV=23, ODD=1
     */
    SPI2->I2SPR = 23UL | (1UL << 8);

    /* Enable RX DMA request in SPI2 */
    SPI2->CR2 |= (1UL << 0); /* RXDMAEN */

    /* 4. Configure DMA1 Channel 1 for Circular Peripheral-to-Memory Transfer */
    DMA1->CH[0].CCR = 0; /* Disable */
    DMA1->CH[0].CPAR = (uint32_t)(&(SPI2->DR));
    DMA1->CH[0].CMAR = (uint32_t)s_dma_audio_buffer;
    DMA1->CH[0].CNDTR = TOTAL_DMA_SAMPLES;
    DMA1->CH[0].CCR = DMA_CCR_CIRC | DMA_CCR_MINC | DMA_CCR_PSIZE_16 | DMA_CCR_MSIZE_16 |
                      DMA_CCR_PL_HIGH | DMA_CCR_TCIE | DMA_CCR_HTIE;

    /* 5. Enable DMA1 Channel 1 Interrupt (IRQ 11) in Cortex-M4 NVIC */
    *((volatile uint32_t *)0xE000E100UL) |= (1UL << 11);
}

void audio_i2s_start(void)
{
    s_ready_buffer = BUFFER_NONE;
    s_is_running = true;
    DMA1->CH[0].CCR |= DMA_CCR_EN;
    SPI2->I2SCFGR |= SPI_I2SCFGR_I2SE;
}

void audio_i2s_stop(void)
{
    s_is_running = false;
    SPI2->I2SCFGR &= ~SPI_I2SCFGR_I2SE;
    DMA1->CH[0].CCR &= ~DMA_CCR_EN;
}

audio_buffer_id_t audio_i2s_get_frame(int16_t **frame_out)
{
    audio_buffer_id_t ready = s_ready_buffer;
    if (ready == BUFFER_PING) {
        *frame_out = &s_dma_audio_buffer[0];
        s_ready_buffer = BUFFER_NONE;
        return BUFFER_PING;
    } else if (ready == BUFFER_PONG) {
        *frame_out = &s_dma_audio_buffer[AUDIO_FRAME_SAMPLES];
        s_ready_buffer = BUFFER_NONE;
        return BUFFER_PONG;
    }
    return BUFFER_NONE;
}

void audio_i2s_dma_half_transfer_callback(void)
{
    s_ready_buffer = BUFFER_PING;
}

void audio_i2s_dma_transfer_callback(void)
{
    s_ready_buffer = BUFFER_PONG;
}

void DMA1_Channel1_IRQHandler(void)
{
    uint32_t isr = DMA1->ISR;
    if (isr & (1UL << 2)) { /* HTIF1 */
        DMA1->IFCR = (1UL << 2);
        audio_i2s_dma_half_transfer_callback();
    }
    if (isr & (1UL << 1)) { /* TCIF1 */
        DMA1->IFCR = (1UL << 1);
        audio_i2s_dma_transfer_callback();
    }
    if (isr & (1UL << 3)) { /* TEIF1 */
        DMA1->IFCR = (1UL << 3);
    }
}

