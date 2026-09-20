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
    __IO uint32_t CR;
    __IO uint32_t ICSCR;
    __IO uint32_t CFGR;
    __IO uint32_t PLLCFGR;
    __IO uint32_t RESERVED0[2];
    __IO uint32_t CIER;
    __IO uint32_t CIFR;
    __IO uint32_t CICR;
    __IO uint32_t SMPSCR;
    __IO uint32_t AHB1ENR;
    __IO uint32_t AHB2ENR;
    __IO uint32_t AHB3ENR;
    __IO uint32_t RESERVED1;
    __IO uint32_t APB1ENR1;
    __IO uint32_t APB1ENR2;
    __IO uint32_t APB2ENR;
    __IO uint32_t APB3ENR;
} RCC_TypeDef;

typedef struct {
    __IO uint32_t CR1;
    __IO uint32_t CR2;
    __IO uint32_t CR3;
    __IO uint32_t CR4;
    __IO uint32_t SR1;
    __IO uint32_t SR2;
    __IO uint32_t SCR;
    __IO uint32_t SUBGHZSPICR;
} PWR_TypeDef;

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

#define GPIOA                   ((GPIO_TypeDef *) GPIOA_BASE)
#define GPIOB                   ((GPIO_TypeDef *) GPIOB_BASE)
#define GPIOC                   ((GPIO_TypeDef *) GPIOC_BASE)
#define SPI2                    ((SPI_TypeDef *) SPI2_BASE)
#define SUBGHZSPI               ((SPI_TypeDef *) SUBGHZSPI_BASE)
#define DMA1                    ((DMA_TypeDef *) DMA1_BASE)
#define RCC                     ((RCC_TypeDef *) RCC_BASE)
#define PWR                     ((PWR_TypeDef *) PWR_BASE)
#define ADC1                    ((ADC_TypeDef *) ADC_BASE)

/* RCC Enable Bits */
#define RCC_AHB1ENR_DMA1EN      (1UL << 0)
#define RCC_AHB2ENR_GPIOAEN     (1UL << 0)
#define RCC_AHB2ENR_GPIOBEN     (1UL << 1)
#define RCC_APB1ENR1_SPI2EN     (1UL << 14)
#define RCC_APB2ENR_ADCEN       (1UL << 9)
#define RCC_APB3ENR_SUBGHZSPIEN (1UL << 0)

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
