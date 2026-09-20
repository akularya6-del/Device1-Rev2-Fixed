/**
 * @file stm32wl55xx.h
 * @brief STM32WL55CC Peripheral Register Definitions
 * Target: Dual-core ARM Cortex-M4 @ 48MHz (Strictly Non-TI)
 */

#ifndef STM32WL55XX_H
#define STM32WL55XX_H

#include <stdint.h>

#define __IO volatile

/* ====================================================================
 * Memory Map Base Addresses
 * ==================================================================== */
#define PERIPH_BASE             0x40000000UL
#define APB1_BASE               (PERIPH_BASE + 0x00000000UL)
#define APB2_BASE               (PERIPH_BASE + 0x00010000UL)
#define AHB1_BASE               (PERIPH_BASE + 0x00020000UL)
#define AHB2_BASE               (PERIPH_BASE + 0x08000000UL)
#define AHB3_BASE               (PERIPH_BASE + 0x18000000UL)

/* APB1 Peripherals */
#define SPI2_BASE               (APB1_BASE + 0x3800UL)

/* APB2 Peripherals */
#define ADC_BASE                (APB2_BASE + 0x2400UL)

/* AHB1 Peripherals */
#define DMA1_BASE               (AHB1_BASE + 0x0000UL)
#define DMAMUX1_BASE            (AHB1_BASE + 0x0800UL)

/* AHB2 Peripherals */
#define GPIOA_BASE              (AHB2_BASE + 0x0000UL)
#define GPIOB_BASE              (AHB2_BASE + 0x0400UL)
#define GPIOC_BASE              (AHB2_BASE + 0x0800UL)

/* AHB3 Peripherals */
#define RCC_BASE                (AHB3_BASE + 0x0000UL)
#define PWR_BASE                (AHB3_BASE + 0x0400UL)
#define EXTI_BASE               (AHB3_BASE + 0x0800UL)
#define SUBGHZSPI_BASE          (AHB3_BASE + 0x10000UL)

/* ====================================================================
 * Peripheral Register Structs
 * ==================================================================== */
typedef struct {
    __IO uint32_t MODER;
    __IO uint32_t OTYPER;
    __IO uint32_t OSPEEDR;
    __IO uint32_t PUPDR;
    __IO uint32_t IDR;
    __IO uint32_t ODR;
    __IO uint32_t BSRR;
    __IO uint32_t LCKR;
    __IO uint32_t AFR[2];
    __IO uint32_t BRR;
} GPIO_TypeDef;

typedef struct {
    __IO uint32_t CR1;
    __IO uint32_t CR2;
    __IO uint32_t SR;
    __IO uint32_t DR;
    __IO uint32_t CRCPR;
    __IO uint32_t RXCRCR;
    __IO uint32_t TXCRCR;
    __IO uint32_t I2SCFGR;
    __IO uint32_t I2SPR;
} SPI_TypeDef;

typedef struct {
    __IO uint32_t CCR;
    __IO uint32_t CNDTR;
    __IO uint32_t CPAR;
    __IO uint32_t CMAR;
} DMA_Channel_TypeDef;

typedef struct {
    __IO uint32_t ISR;
    __IO uint32_t IFCR;
    DMA_Channel_TypeDef CH[7];
} DMA_TypeDef;

typedef struct {
    __IO uint32_t CR;           /* 0x00 */
    __IO uint32_t ICSCR;        /* 0x04 */
    __IO uint32_t CFGR;         /* 0x08 */
    __IO uint32_t PLLCFGR;      /* 0x0C */
    uint32_t RESERVED0;         /* 0x10 */
    uint32_t RESERVED1;         /* 0x14 */
    __IO uint32_t CIER;         /* 0x18 */
    __IO uint32_t CIFR;         /* 0x1C */
    __IO uint32_t CICR;         /* 0x20 */
    uint32_t RESERVED2;         /* 0x24 */
    __IO uint32_t AHB1RSTR;     /* 0x28 */
    __IO uint32_t AHB2RSTR;     /* 0x2C */
    __IO uint32_t AHB3RSTR;     /* 0x30 */
    uint32_t RESERVED3;         /* 0x34 */
    __IO uint32_t APB1RSTR1;    /* 0x38 */
    __IO uint32_t APB1RSTR2;    /* 0x3C */
    __IO uint32_t APB2RSTR;     /* 0x40 */
    __IO uint32_t APB3RSTR;     /* 0x44 */
    __IO uint32_t AHB1ENR;      /* 0x48 */
    __IO uint32_t AHB2ENR;      /* 0x4C */
    __IO uint32_t AHB3ENR;      /* 0x50 */
    uint32_t RESERVED4;         /* 0x54 */
    __IO uint32_t APB1ENR1;     /* 0x58 */
    __IO uint32_t APB1ENR2;     /* 0x5C */
    __IO uint32_t APB2ENR;      /* 0x60 */
    __IO uint32_t APB3ENR;      /* 0x64 */
    __IO uint32_t AHB1SMENR;    /* 0x68 */
    __IO uint32_t AHB2SMENR;    /* 0x6C */
    __IO uint32_t AHB3SMENR;    /* 0x70 */
    uint32_t RESERVED5;         /* 0x74 */
    __IO uint32_t APB1SMENR1;   /* 0x78 */
    __IO uint32_t APB1SMENR2;   /* 0x7C */
    __IO uint32_t APB2SMENR;    /* 0x80 */
    __IO uint32_t APB3SMENR;    /* 0x84 */
    __IO uint32_t CCIPR;        /* 0x88 */
    uint32_t RESERVED6;         /* 0x8C */
    __IO uint32_t BDCR;         /* 0x90 */
    __IO uint32_t CSR;          /* 0x94 */
} RCC_TypeDef;

typedef struct {
    __IO uint32_t CR1;          /* 0x00 */
    __IO uint32_t CR2;          /* 0x04 */
    __IO uint32_t CR3;          /* 0x08 */
    __IO uint32_t CR4;          /* 0x0C */
    __IO uint32_t SR1;          /* 0x10 */
    __IO uint32_t SR2;          /* 0x14 */
    __IO uint32_t SCR;          /* 0x18 */
    __IO uint32_t CR5;          /* 0x1C */
    __IO uint32_t PUCRA;        /* 0x20 */
    __IO uint32_t PDCRA;        /* 0x24 */
    __IO uint32_t PUCRB;        /* 0x28 */
    __IO uint32_t PDCRB;        /* 0x2C */
    __IO uint32_t PUCRC;        /* 0x30 */
    __IO uint32_t PDCRC;        /* 0x34 */
    uint32_t RESERVED0[8];      /* 0x38-0x54 */
    __IO uint32_t PUCRH;        /* 0x58 */
    __IO uint32_t PDCRH;        /* 0x5C */
    uint32_t RESERVED1[8];      /* 0x60-0x7C */
    __IO uint32_t C2CR1;        /* 0x80 */
    __IO uint32_t C2CR3;        /* 0x84 */
    __IO uint32_t EXTSCR;       /* 0x88 */
    __IO uint32_t SECCFGR;      /* 0x8C */
    __IO uint32_t SUBGHZSPICR;  /* 0x90 */
} PWR_TypeDef;

typedef struct {
    __IO uint32_t ACR;          /* 0x00 */
} FLASH_TypeDef;

typedef struct {
    __IO uint32_t CCR;          /* 0x00 */
} DMAMUX_Channel_TypeDef;

typedef struct {
    __IO uint32_t ISR;
    __IO uint32_t IER;
    __IO uint32_t CR;
    __IO uint32_t CFGR1;
    __IO uint32_t CFGR2;
    __IO uint32_t SMPR;
    __IO uint32_t RESERVED0[2];
    __IO uint32_t CHSELR;
    __IO uint32_t DR;
    __IO uint32_t CALFACT;
    __IO uint32_t CCR;
} ADC_TypeDef;

#define FLASH_BASE              0x58004000UL
#define GPIOA                   ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB                   ((GPIO_TypeDef *) GPIOB_BASE)
#define GPIOC                   ((GPIO_TypeDef *) GPIOC_BASE)
#define SPI2                    ((SPI_TypeDef *) SPI2_BASE)
#define SUBGHZSPI               ((SPI_TypeDef *) SUBGHZSPI_BASE)
#define DMA1                    ((DMA_TypeDef *) DMA1_BASE)
#define DMAMUX1_Channel0        ((DMAMUX_Channel_TypeDef *) DMAMUX1_BASE)
#define RCC                     ((RCC_TypeDef *) RCC_BASE)
#define PWR                     ((PWR_TypeDef *) PWR_BASE)
#define FLASH                   ((FLASH_TypeDef *) FLASH_BASE)
#define ADC1                    ((ADC_TypeDef *) ADC_BASE)

/* RCC Enable Bits */
#define RCC_AHB1ENR_DMA1EN      (1UL << 0)
#define RCC_AHB1ENR_DMAMUX1EN   (1UL << 2)
#define RCC_AHB2ENR_GPIOAEN     (1UL << 0)
#define RCC_AHB2ENR_GPIOBEN     (1UL << 1)
#define RCC_AHB3ENR_FLASHEN     (1UL << 7)
#define RCC_APB1ENR1_SPI2EN     (1UL << 14)
#define RCC_APB2ENR_ADCEN       (1UL << 9)
#define RCC_APB3ENR_SUBGHZSPIEN (1UL << 0)

/* RCC CR & CFGR Clock Config Bits */
#define RCC_CR_MSION            (1UL << 0)
#define RCC_CR_MSIRDY           (1UL << 1)
#define RCC_CR_HSEON            (1UL << 16)
#define RCC_CR_HSERDY           (1UL << 17)
#define RCC_CR_HSEBYP           (1UL << 18)
#define RCC_CR_PLLON            (1UL << 24)
#define RCC_CR_PLLRDY           (1UL << 25)

#define RCC_PLLCFGR_PLLSRC_HSE  (3UL << 0)
#define RCC_PLLCFGR_PLLM_DIV2   (1UL << 4)
#define RCC_PLLCFGR_PLLREN      (1UL << 28)
#define RCC_PLLCFGR_PLLR_DIV2   (1UL << 29)

#define RCC_CFGR_SW_PLL         (3UL << 0)
#define RCC_CFGR_SWS_PLL        (3UL << 2)

/* FLASH ACR Wait States */
#define FLASH_ACR_LATENCY_2WS   (2UL << 0)

/* PWR Control & Status Bits */
#define PWR_CR1_VOS_RANGE1      (1UL << 9)
#define PWR_SR2_RFBUSYS         (1UL << 1)
#define PWR_SUBGHZSPICR_NSS     (1UL << 15)

/* DMAMUX Request IDs */
#define DMAMUX_REQ_SPI2_RX      9UL

/* I2S Configuration Bits */
#define SPI_I2SCFGR_I2SMOD      (1UL << 11)
#define SPI_I2SCFGR_I2SE        (1UL << 10)
#define SPI_I2SCFGR_I2SCFG_MRX  (3UL << 8)  /* Master Receive */
#define SPI_I2SCFGR_I2SSTD_PH   (0UL << 4)  /* Philips Standard */
#define SPI_I2SCFGR_DATLEN_16   (0UL << 1)  /* 16-bit data */
#define SPI_I2SCFGR_CHLEN_32    (1UL << 0)  /* 32-bit frame channel length */

/* DMA Channel Configuration Bits */
#define DMA_CCR_EN             (1UL << 0)
#define DMA_CCR_TCIE           (1UL << 1)
#define DMA_CCR_HTIE           (1UL << 2)
#define DMA_CCR_CIRC           (1UL << 5)
#define DMA_CCR_PINC           (1UL << 6)
#define DMA_CCR_MINC           (1UL << 7)
#define DMA_CCR_PSIZE_16       (1UL << 8)
#define DMA_CCR_MSIZE_16       (1UL << 10)
#define DMA_CCR_PL_HIGH        (2UL << 12)

#endif /* STM32WL55XX_H */

