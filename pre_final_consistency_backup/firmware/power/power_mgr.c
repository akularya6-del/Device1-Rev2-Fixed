/**
 * @file power_mgr.c
 * @brief Real Power Management Driver Implementation for STM32WL55
 */

#include "power_mgr.h"
#include "hardware_config.h"
#include "stm32wl55xx.h"

/* Factory calibration register for internal VREFINT at 30°C / 3.3V */
#define VREFINT_CAL_ADDR        ((uint16_t*)((uint32_t)0x1FFF75AA))
#define VREFINT_CAL_VOLTAGE_MV  3300U

static power_status_t s_current_status = {
    .millivolts = 3700,
    .level = BATTERY_NOMINAL,
    .is_charging = false
};

void power_mgr_init(void)
{
    /* 1. Enable GPIOA and ADC1 peripheral clocks */
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_ADCEN;

    /* 2. Configure PA0 as Input with internal Pull-Up (MCP73831 STAT pin) */
    GPIOA->MODER &= ~(3UL << (0 * 2)); /* Input mode (00) */
    GPIOA->PUPDR &= ~(3UL << (0 * 2));
    GPIOA->PUPDR |=  (1UL << (0 * 2)); /* Pull-Up (01) */

    /* 3. Enable Internal Reference Voltage VREFINT */
    ADC1->CCR |= (1UL << 22); /* VREFEN */

    /* 4. Enable ADC Voltage Regulator and Calibrate */
    ADC1->CR &= ~(1UL << 0); /* ADEN = 0 */
    ADC1->CR |= (1UL << 28); /* ADVREGEN = 1 */
    for (volatile int i = 0; i < 1000; i++) {} /* Regulator startup delay */

    ADC1->CR |= (1UL << 31); /* ADCAL */
    while (ADC1->CR & (1UL << 31)) {} /* Wait calibration complete */

    /* Enable ADC */
    ADC1->ISR |= (1UL << 0); /* Clear ADRDY */
    ADC1->CR |= (1UL << 0);  /* ADEN = 1 */
    while (!(ADC1->ISR & (1UL << 0))) {} /* Wait ADRDY */
}

void power_mgr_update(power_status_t *status)
{
    if (!status) return;

    /* 1. Read Charging Status from MCP73831 STAT pin (PA0: Active-Low while charging) */
    bool charging = !(GPIOA->IDR & (1UL << 0));
    s_current_status.is_charging = charging;

    /* 2. Trigger Single-Shot ADC Conversion on VREFINT channel */
    ADC1->CHSELR = (1UL << 0); /* Select Channel 0 (VREFINT) */
    ADC1->ISR |= (1UL << 2);   /* Clear EOC */
    ADC1->CR |= (1UL << 2);    /* ADSTART */

    uint32_t timeout = 10000;
    while (!(ADC1->ISR & (1UL << 2)) && --timeout) {}

    if (timeout > 0) {
        uint16_t adc_raw = (uint16_t)ADC1->DR;
        if (adc_raw > 0) {
            uint16_t vref_cal = *VREFINT_CAL_ADDR;
            if (vref_cal == 0xFFFF || vref_cal == 0) {
                vref_cal = 1660; /* Nominal 12-bit code for 1.212V @ 3.0V */
            }
            s_current_status.millivolts = (uint16_t)((VREFINT_CAL_VOLTAGE_MV * (uint32_t)vref_cal) / adc_raw);
        }
    }

    /* 3. Evaluate Battery Voltage Level */
    if (s_current_status.millivolts > 3800) {
        s_current_status.level = BATTERY_FULL;
    } else if (s_current_status.millivolts > 3400) {
        s_current_status.level = BATTERY_NOMINAL;
    } else if (s_current_status.millivolts > 3200) {
        s_current_status.level = BATTERY_LOW;
    } else {
        s_current_status.level = BATTERY_CRITICAL;
    }

    *status = s_current_status;
}

void power_mgr_sleep(uint32_t sleep_duration_ms)
{
    (void)sleep_duration_ms;
    /* Cortex-M4 Wait For Interrupt (Sleep mode) */
    __asm volatile("wfi");
}
