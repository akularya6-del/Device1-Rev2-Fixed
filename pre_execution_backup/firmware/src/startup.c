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
    SysTick_Handler
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
