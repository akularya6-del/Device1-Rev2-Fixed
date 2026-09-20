/**
 * @file startup.c
 * @brief Vector table, startup routines, and AEABI helpers for STM32WL55CCU6 (Cortex-M4)
 */

#include <stdint.h>
#include <stddef.h>

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern int main(void);

void Reset_Handler(void);
void Default_Handler(void);

/* Weak Aliases for Standard Cortex-M4 Exceptions */
void NMI_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void MemManage_Handler(void)  __attribute__((weak, alias("Default_Handler")));
void BusFault_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void UsageFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void)        __attribute__((weak, alias("Default_Handler")));
void DebugMon_Handler(void)   __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void)     __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void)    __attribute__((weak, alias("Default_Handler")));

/* Weak Aliases for STM32WL55 Peripheral Interrupts (62 IRQs) */
void WWDG_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void PVD_PVM_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void TAMP_STAMP_LSECSS_SSRU_IRQHandler(void) __attribute__((weak, alias("Default_Handler")));
void RTC_WKUP_IRQHandler(void)               __attribute__((weak, alias("Default_Handler")));
void FLASH_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void RCC_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void EXTI0_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void EXTI1_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void EXTI2_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void EXTI3_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void EXTI4_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel1_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel2_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel3_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel4_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel5_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel6_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA1_Channel7_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void ADC_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void DAC_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void C2SEV_PWR_C2H_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void COMP_IRQHandler(void)                   __attribute__((weak, alias("Default_Handler")));
void EXTI9_5_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void TIM1_BRK_IRQHandler(void)               __attribute__((weak, alias("Default_Handler")));
void TIM1_UP_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void TIM1_TRG_COM_IRQHandler(void)           __attribute__((weak, alias("Default_Handler")));
void TIM1_CC_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void TIM2_IRQHandler(void)                   __attribute__((weak, alias("Default_Handler")));
void TIM16_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void TIM17_IRQHandler(void)                  __attribute__((weak, alias("Default_Handler")));
void I2C1_EV_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void I2C1_ER_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void I2C2_EV_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void I2C2_ER_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void SPI1_IRQHandler(void)                   __attribute__((weak, alias("Default_Handler")));
void SPI2_IRQHandler(void)                   __attribute__((weak, alias("Default_Handler")));
void USART1_IRQHandler(void)                 __attribute__((weak, alias("Default_Handler")));
void USART2_IRQHandler(void)                 __attribute__((weak, alias("Default_Handler")));
void LPUART1_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void LPTIM1_IRQHandler(void)                 __attribute__((weak, alias("Default_Handler")));
void LPTIM2_IRQHandler(void)                 __attribute__((weak, alias("Default_Handler")));
void EXTI15_10_IRQHandler(void)              __attribute__((weak, alias("Default_Handler")));
void RTC_Alarm_IRQHandler(void)              __attribute__((weak, alias("Default_Handler")));
void LPTIM3_IRQHandler(void)                 __attribute__((weak, alias("Default_Handler")));
void SUBGHZSPI_IRQHandler(void)              __attribute__((weak, alias("Default_Handler")));
void IPCC_C1_RX_IRQHandler(void)             __attribute__((weak, alias("Default_Handler")));
void IPCC_C1_TX_IRQHandler(void)             __attribute__((weak, alias("Default_Handler")));
void HSEM_IRQHandler(void)                   __attribute__((weak, alias("Default_Handler")));
void I2C3_EV_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void I2C3_ER_IRQHandler(void)                __attribute__((weak, alias("Default_Handler")));
void SUBGHZ_Radio_IRQHandler(void)           __attribute__((weak, alias("Default_Handler")));
void AES_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void RNG_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void PKA_IRQHandler(void)                    __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel1_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel2_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel3_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel4_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel5_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel6_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMA2_Channel7_IRQHandler(void)          __attribute__((weak, alias("Default_Handler")));
void DMAMUX1_OVR_IRQHandler(void)            __attribute__((weak, alias("Default_Handler")));

/* Vector Table */
__attribute__((section(".isr_vector")))
const void *g_pfnVectors[] = {
    &_estack,
    Reset_Handler,
    NMI_Handler,
    HardFault_Handler,
    MemManage_Handler,
    BusFault_Handler,
    UsageFault_Handler,
    0, 0, 0, 0,             /* Reserved */
    SVC_Handler,
    DebugMon_Handler,
    0,                      /* Reserved */
    PendSV_Handler,
    SysTick_Handler,

    /* STM32WL55 External Interrupts (Cortex-M4) */
    WWDG_IRQHandler,                    /* 16: IRQ 0 */
    PVD_PVM_IRQHandler,                 /* 17: IRQ 1 */
    TAMP_STAMP_LSECSS_SSRU_IRQHandler,  /* 18: IRQ 2 */
    RTC_WKUP_IRQHandler,                /* 19: IRQ 3 */
    FLASH_IRQHandler,                   /* 20: IRQ 4 */
    RCC_IRQHandler,                     /* 21: IRQ 5 */
    EXTI0_IRQHandler,                   /* 22: IRQ 6 */
    EXTI1_IRQHandler,                   /* 23: IRQ 7 */
    EXTI2_IRQHandler,                   /* 24: IRQ 8 */
    EXTI3_IRQHandler,                   /* 25: IRQ 9 */
    EXTI4_IRQHandler,                   /* 26: IRQ 10 */
    DMA1_Channel1_IRQHandler,           /* 27: IRQ 11 */
    DMA1_Channel2_IRQHandler,           /* 28: IRQ 12 */
    DMA1_Channel3_IRQHandler,           /* 29: IRQ 13 */
    DMA1_Channel4_IRQHandler,           /* 30: IRQ 14 */
    DMA1_Channel5_IRQHandler,           /* 31: IRQ 15 */
    DMA1_Channel6_IRQHandler,           /* 32: IRQ 16 */
    DMA1_Channel7_IRQHandler,           /* 33: IRQ 17 */
    ADC_IRQHandler,                     /* 34: IRQ 18 */
    DAC_IRQHandler,                     /* 35: IRQ 19 */
    C2SEV_PWR_C2H_IRQHandler,           /* 36: IRQ 20 */
    COMP_IRQHandler,                    /* 37: IRQ 21 */
    EXTI9_5_IRQHandler,                 /* 38: IRQ 22 */
    TIM1_BRK_IRQHandler,                /* 39: IRQ 23 */
    TIM1_UP_IRQHandler,                 /* 40: IRQ 24 */
    TIM1_TRG_COM_IRQHandler,            /* 41: IRQ 25 */
    TIM1_CC_IRQHandler,                 /* 42: IRQ 26 */
    TIM2_IRQHandler,                    /* 43: IRQ 27 */
    TIM16_IRQHandler,                   /* 44: IRQ 28 */
    TIM17_IRQHandler,                   /* 45: IRQ 29 */
    I2C1_EV_IRQHandler,                 /* 46: IRQ 30 */
    I2C1_ER_IRQHandler,                 /* 47: IRQ 31 */
    I2C2_EV_IRQHandler,                 /* 48: IRQ 32 */
    I2C2_ER_IRQHandler,                 /* 49: IRQ 33 */
    SPI1_IRQHandler,                    /* 50: IRQ 34 */
    SPI2_IRQHandler,                    /* 51: IRQ 35 */
    USART1_IRQHandler,                  /* 52: IRQ 36 */
    USART2_IRQHandler,                  /* 53: IRQ 37 */
    LPUART1_IRQHandler,                 /* 54: IRQ 38 */
    LPTIM1_IRQHandler,                  /* 55: IRQ 39 */
    LPTIM2_IRQHandler,                  /* 56: IRQ 40 */
    EXTI15_10_IRQHandler,               /* 57: IRQ 41 */
    RTC_Alarm_IRQHandler,               /* 58: IRQ 42 */
    LPTIM3_IRQHandler,                  /* 59: IRQ 43 */
    SUBGHZSPI_IRQHandler,               /* 60: IRQ 44 */
    IPCC_C1_RX_IRQHandler,              /* 61: IRQ 45 */
    IPCC_C1_TX_IRQHandler,              /* 62: IRQ 46 */
    HSEM_IRQHandler,                    /* 63: IRQ 47 */
    I2C3_EV_IRQHandler,                 /* 64: IRQ 48 */
    I2C3_ER_IRQHandler,                 /* 65: IRQ 49 */
    SUBGHZ_Radio_IRQHandler,            /* 66: IRQ 50 */
    AES_IRQHandler,                     /* 67: IRQ 51 */
    RNG_IRQHandler,                     /* 68: IRQ 52 */
    PKA_IRQHandler,                     /* 69: IRQ 53 */
    DMA2_Channel1_IRQHandler,           /* 70: IRQ 54 */
    DMA2_Channel2_IRQHandler,           /* 71: IRQ 55 */
    DMA2_Channel3_IRQHandler,           /* 72: IRQ 56 */
    DMA2_Channel4_IRQHandler,           /* 73: IRQ 57 */
    DMA2_Channel5_IRQHandler,           /* 74: IRQ 58 */
    DMA2_Channel6_IRQHandler,           /* 75: IRQ 59 */
    DMA2_Channel7_IRQHandler,           /* 76: IRQ 60 */
    DMAMUX1_OVR_IRQHandler              /* 77: IRQ 61 */
};


/* AEABI helper implementations for freestanding ARM */
void __aeabi_memcpy(void *dest, const void *src, size_t n)
{
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;
    while (n--) {
        *d++ = *s++;
    }
}

void __aeabi_memcpy4(void *dest, const void *src, size_t n)
{
    __aeabi_memcpy(dest, src, n);
}

void __aeabi_memclr(void *dest, size_t n)
{
    unsigned char *d = (unsigned char *)dest;
    while (n--) {
        *d++ = 0;
    }
}

void __aeabi_memclr4(void *dest, size_t n)
{
    __aeabi_memclr(dest, n);
}

void __aeabi_memset(void *dest, size_t n, int c)
{
    unsigned char *d = (unsigned char *)dest;
    while (n--) {
        *d++ = (unsigned char)c;
    }
}

void Reset_Handler(void)
{
    /* Initialize .data section from Flash to RAM */
    uint32_t *pSrc = &_sidata;
    uint32_t *pDest = &_sdata;
    while (pDest < &_edata) {
        *pDest++ = *pSrc++;
    }

    /* Zero initialize .bss section in RAM */
    pDest = &_sbss;
    while (pDest < &_ebss) {
        *pDest++ = 0;
    }

    /* Call application entry point */
    main();

    /* Trap if main exits */
    while (1) {}
}

void Default_Handler(void)
{
    while (1) {}
}
