/**
 * @file subghz_radio.c
 * @brief Real Sub-GHz Radio Driver Implementation for STM32WL55
 * SX126x-compatible core Sub-GHz transceiver commands and packet engine.
 * Target: 868.0 MHz, 150 kbps 2-GFSK, +14 dBm High-Power PA
 */

#include "subghz_radio.h"
#include "hardware_config.h"
#include "stm32wl55xx.h"
#include <string.h>

/* SX126x / STM32WL Radio OpCodes */
#define RADIO_SET_SLEEP                 0x84
#define RADIO_SET_STANDBY               0x80
#define RADIO_SET_PACKETTYPE            0x8A
#define RADIO_SET_RFFREQUENCY           0x86
#define RADIO_SET_PACONFIG              0x95
#define RADIO_SET_TXPARAMS              0x8E
#define RADIO_SET_BUFFERBASEADDRESS     0x8F
#define RADIO_SET_MODULATIONPARAMS      0x8B
#define RADIO_SET_PACKETPARAMS          0x8C
#define RADIO_SET_TX                    0x83
#define RADIO_SET_RX                    0x82
#define RADIO_GET_STATUS                0xC0
#define RADIO_GET_IRQSTATUS             0x12
#define RADIO_CLEAR_IRQSTATUS           0x02
#define RADIO_WRITE_BUFFER              0x0E
#define RADIO_READ_BUFFER               0x1E
#define RADIO_WRITE_REGISTER            0x0D
#define RADIO_READ_REGISTER             0x1D

#define PACKET_TYPE_GFSK                0x00

/* IRQ Status Bits */
#define IRQ_TX_DONE                     (1U << 0)
#define IRQ_RX_DONE                     (1U << 1)
#define IRQ_PREAMBLE_DETECTED           (1U << 2)
#define IRQ_SYNCWORD_VALID              (1U << 3)
#define IRQ_HEADER_VALID                (1U << 4)
#define IRQ_HEADER_ERR                  (1U << 5)
#define IRQ_CRC_ERR                     (1U << 6)
#define IRQ_TIMEOUT                     (1U << 9)

static radio_audio_packet_t s_tx_packet;
static bool s_radio_initialized = false;

/* ====================================================================
 * Low-Level SUBGHZSPI Interface Helpers
 * ==================================================================== */
static inline void subghz_wait_on_busy(void)
{
    uint32_t timeout = 100000;
    while ((PWR->SR2 & PWR_SR2_RFBUSYS) && --timeout) {}
}

static inline void subghz_nss_low(void)
{
    subghz_wait_on_busy();
    PWR->SUBGHZSPICR &= ~PWR_SUBGHZSPICR_NSS; /* Drive Radio NSS Low */
}

static inline void subghz_nss_high(void)
{
    PWR->SUBGHZSPICR |= PWR_SUBGHZSPICR_NSS;  /* Drive Radio NSS High */
    subghz_wait_on_busy();
}

static uint8_t subghz_spi_transfer(uint8_t byte)
{
    while (!(SUBGHZSPI->SR & (1UL << 1))) {} /* Wait TXE */
    *(volatile uint8_t *)&SUBGHZSPI->DR = byte;
    while (!(SUBGHZSPI->SR & (1UL << 0))) {} /* Wait RXNE */
    return *(volatile uint8_t *)&SUBGHZSPI->DR;
}

static void subghz_write_cmd(uint8_t opcode, const uint8_t *params, uint16_t len)
{
    subghz_nss_low();
    subghz_spi_transfer(opcode);
    for (uint16_t i = 0; i < len; i++) {
        subghz_spi_transfer(params[i]);
    }
    subghz_nss_high();
}

static void subghz_read_cmd(uint8_t opcode, uint8_t *data, uint16_t len)
{
    subghz_nss_low();
    subghz_spi_transfer(opcode);
    subghz_spi_transfer(0x00); /* NOP / Status */
    for (uint16_t i = 0; i < len; i++) {
        data[i] = subghz_spi_transfer(0x00);
    }
    subghz_nss_high();
}

static void subghz_write_buf(uint8_t offset, const uint8_t *data, uint16_t len)
{
    subghz_nss_low();
    subghz_spi_transfer(RADIO_WRITE_BUFFER);
    subghz_spi_transfer(offset);
    for (uint16_t i = 0; i < len; i++) {
        subghz_spi_transfer(data[i]);
    }
    subghz_nss_high();
}

static void subghz_read_buf(uint8_t offset, uint8_t *data, uint16_t len)
{
    subghz_nss_low();
    subghz_spi_transfer(RADIO_READ_BUFFER);
    subghz_spi_transfer(offset);
    subghz_spi_transfer(0x00); /* Status */
    for (uint16_t i = 0; i < len; i++) {
        data[i] = subghz_spi_transfer(0x00);
    }
    subghz_nss_high();
}


/* ====================================================================
 * High-Level Radio API Implementation
 * ==================================================================== */
bool subghz_radio_init(void)
{
    /* 1. Enable Clocks for SUBGHZSPI and PWR */
    RCC->APB3ENR |= RCC_APB3ENR_SUBGHZSPIEN;
    subghz_nss_high();

    /* Configure SUBGHZSPI: Master, Baud = SYSCLK / 4 = 12 MHz, 8-bit, Mode 0 */
    SUBGHZSPI->CR1 = (1UL << 2) | (1UL << 3); /* MSTR, BR = /4 */
    SUBGHZSPI->CR2 = (7UL << 8) | (1UL << 12); /* DS = 8-bit, FRXTH = 8-bit */
    SUBGHZSPI->CR1 |= (1UL << 6); /* SPE (Enable SPI) */

    /* 2. Standby RC mode */
    uint8_t standby_param = 0x00; /* STDBY_RC */
    subghz_write_cmd(RADIO_SET_STANDBY, &standby_param, 1);

    /* 3. Set Packet Type: 2-GFSK */
    uint8_t pkt_type = PACKET_TYPE_GFSK;
    subghz_write_cmd(RADIO_SET_PACKETTYPE, &pkt_type, 1);

    /* 4. Set RF Frequency: 868.0 MHz
     * Freq_reg = (868,000,000 * 2^25) / 32,000,000 = 910163968 = 0x36400000
     */
    uint8_t rf_freq[4] = { 0x36, 0x40, 0x00, 0x00 };
    subghz_write_cmd(RADIO_SET_RFFREQUENCY, rf_freq, 4);

    /* 5. Set PA Config for High-Power PA (+14 dBm)
     * dutyCycle=0x04, hpMax=0x07, deviceSel=0x00, paLut=0x01
     */
    uint8_t pa_config[4] = { 0x04, 0x07, 0x00, 0x01 };
    subghz_write_cmd(RADIO_SET_PACONFIG, pa_config, 4);

    /* 6. Set Tx Params: +14 dBm, 40us ramp time */
    uint8_t tx_params[2] = { 0x0E, 0x02 };
    subghz_write_cmd(RADIO_SET_TXPARAMS, tx_params, 2);

    /* 7. Set Modulation Params:
     * Bitrate = 150,000 bps -> br = 32 * 32000000 / 150000 = 6827 = 0x001AAB
     * PulseShape = 0x09 (Gaussian BT=0.5)
     * RxBW = 0x19 (234.3 kHz DSB)
     * Fdev = 37,500 Hz -> (37500 * 2^25) / 32000000 = 39321 = 0x009999
     */
    uint8_t mod_params[8] = {
        0x00, 0x1A, 0xAB,   /* Bitrate = 150 kbps */
        0x09,               /* PulseShape BT = 0.5 */
        0x19,               /* RxBandwidth = 234.3 kHz */
        0x00, 0x99, 0x99    /* Fdev = 37.5 kHz */
    };
    subghz_write_cmd(RADIO_SET_MODULATIONPARAMS, mod_params, 8);

    /* 8. Set Packet Params:
     * Preamble = 32 bits (0x0020)
     * PreambleDetector = 0x04 (16-bit)
     * SyncWordLength = 16 bits (0x10)
     * AddrComp = 0x00 (None)
     * PacketType = 0x00 (Variable length)
     * PayloadLength = sizeof(radio_audio_packet_t) = 72 bytes
     * CRCType = 0x02 (2 Bytes CCITT)
     * Whitening = 0x01 (Enabled)
     */
    uint8_t pkt_params[9] = {
        0x00, 0x20,         /* Preamble length (32 bits) */
        0x04,               /* Preamble detector length (16 bits) */
        0x10,               /* Syncword length (16 bits) */
        0x00,               /* AddrComp off */
        0x00,               /* Variable length payload */
        sizeof(radio_audio_packet_t), /* Payload length */
        0x02,               /* 2-Byte CRC (CRC-CCITT) */
        0x01                /* Whitening enabled */
    };
    subghz_write_cmd(RADIO_SET_PACKETPARAMS, pkt_params, 9);

    /* 9. Set Sync Word: 0x2DD4 */
    uint8_t sync_cmd[5] = { 0x06, 0xC0, RF_SYNC_WORD_0, RF_SYNC_WORD_1, 0x00 };
    subghz_write_cmd(RADIO_WRITE_REGISTER, sync_cmd, 5);

    /* 10. Set Buffer Base Address: TX=0, RX=128 */
    uint8_t buf_base[2] = { 0x00, 0x80 };
    subghz_write_cmd(RADIO_SET_BUFFERBASEADDRESS, buf_base, 2);

    s_radio_initialized = true;
    return true;
}

bool subghz_radio_send_frame(uint8_t seq, int16_t valprev, int8_t index, const uint8_t *adpcm_data)
{
    if (!s_radio_initialized || !adpcm_data) {
        return false;
    }

    /* Build packet header */
    s_tx_packet.header.magic = PACKET_MAGIC;
    s_tx_packet.header.type = PACKET_TYPE_AUDIO;
    s_tx_packet.header.seq_num = seq;
    s_tx_packet.header.valprev = valprev;
    s_tx_packet.header.index = index;
    s_tx_packet.header.payload_len = AUDIO_FRAME_BYTES_ADPCM;

    /* Copy compressed payload */
    memcpy(s_tx_packet.payload, adpcm_data, AUDIO_FRAME_BYTES_ADPCM);

    /* Write packet to Radio TX Buffer (offset 0) */
    subghz_write_buf(0x00, (const uint8_t *)&s_tx_packet, sizeof(s_tx_packet));

    /* Clear IRQ status */
    uint8_t clr_irq[2] = { 0xFF, 0xFF };
    subghz_write_cmd(RADIO_CLEAR_IRQSTATUS, clr_irq, 2);

    /* Trigger Transmit with 10ms timeout (150kbps airtime = 4.27ms)
     * Timeout = 10ms / 15.625us = 640 = 0x000280
     */
    uint8_t tx_timeout[3] = { 0x00, 0x02, 0x80 };
    subghz_write_cmd(RADIO_SET_TX, tx_timeout, 3);

    return true;
}

bool subghz_radio_receive_ack(uint8_t *cmd_received, uint32_t timeout_us)
{
    if (!s_radio_initialized || !cmd_received) {
        return false;
    }
    *cmd_received = CMD_ACK_NONE;

    /* Set Radio to RX mode with specified timeout */
    uint32_t ticks = timeout_us / 16U;
    uint8_t rx_timeout[3] = { (uint8_t)(ticks >> 16), (uint8_t)(ticks >> 8), (uint8_t)ticks };
    subghz_write_cmd(RADIO_SET_RX, rx_timeout, 3);

    /* Check IRQ status */
    uint8_t irq_status[2] = { 0, 0 };
    subghz_read_cmd(RADIO_GET_IRQSTATUS, irq_status, 2);
    uint16_t irq = ((uint16_t)irq_status[0] << 8) | irq_status[1];

    if ((irq & IRQ_RX_DONE) && !(irq & IRQ_CRC_ERR)) {
        /* Read received ACK packet from RX buffer (offset 128) */
        uint8_t rx_buf[16];
        subghz_read_buf(0x80, rx_buf, sizeof(rx_buf));
        radio_header_t *hdr = (radio_header_t *)rx_buf;
        if (hdr->magic == PACKET_MAGIC && hdr->type == PACKET_TYPE_ACK) {
            *cmd_received = rx_buf[sizeof(radio_header_t)];
            return true;
        }
    }

    return false;
}

void subghz_radio_sleep(void)
{
    uint8_t sleep_cfg = 0x00; /* Cold start sleep */
    subghz_write_cmd(RADIO_SET_SLEEP, &sleep_cfg, 1);
}
