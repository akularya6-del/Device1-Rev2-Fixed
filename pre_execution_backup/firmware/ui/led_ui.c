/**
 * @file led_ui.c
 * @brief Real LED UI Driver Implementation for STM32WL55
 * Controls Bi-Color Red (PA4) / Blue (PA5) LED.
 */

#include "led_ui.h"
#include "hardware_config.h"
#include "stm32wl55xx.h"

static bool s_red_state = false;
static bool s_blue_state = false;

static uint8_t  s_remaining_flashes = 0;
static uint32_t s_flash_timer_ms = 0;
static bool     s_flash_phase = false;

#define FLASH_ON_TIME_MS    100U
#define FLASH_OFF_TIME_MS   120U

void led_ui_init(void)
{
    /* Enable GPIOA clock */
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;

    /* Configure PA4 (LED_R) as Output Push-Pull, Low-speed */
    GPIOA->MODER &= ~(3UL << (LED_R_PIN * 2));
    GPIOA->MODER |=  (1UL << (LED_R_PIN * 2)); /* General Purpose Output (01) */
    GPIOA->OTYPER &= ~(1UL << LED_R_PIN);      /* Push-Pull (0) */

    /* Configure PA5 (LED_B) as Output Push-Pull, Low-speed */
    GPIOA->MODER &= ~(3UL << (LED_B_PIN * 2));
    GPIOA->MODER |=  (1UL << (LED_B_PIN * 2));
    GPIOA->OTYPER &= ~(1UL << LED_B_PIN);

    /* Turn both off initially (Cathode to GND, so Low = OFF) */
    led_ui_set_red(false);
    led_ui_set_blue(false);

    s_remaining_flashes = 0;
    s_flash_timer_ms = 0;
    s_flash_phase = false;
}

void led_ui_set_red(bool on)
{
    s_red_state = on;
    if (on) {
        GPIOA->BSRR = (1UL << LED_R_PIN);          /* Set PA4 High (ON) */
    } else {
        GPIOA->BSRR = (1UL << (LED_R_PIN + 16));   /* Reset PA4 Low (OFF) */
    }
}

void led_ui_set_blue(bool on)
{
    s_blue_state = on;
    if (on) {
        GPIOA->BSRR = (1UL << LED_B_PIN);          /* Set PA5 High (ON) */
    } else {
        GPIOA->BSRR = (1UL << (LED_B_PIN + 16));   /* Reset PA5 Low (OFF) */
    }
}

void led_ui_indicate_cmd(uint8_t cmd_code)
{
    switch (cmd_code) {
        case CMD_OPTION_A:
            s_remaining_flashes = 1;
            break;
        case CMD_OPTION_B:
            s_remaining_flashes = 2;
            break;
        case CMD_OPTION_C:
            s_remaining_flashes = 3;
            break;
        case CMD_OPTION_D:
            s_remaining_flashes = 4;
            break;
        default:
            s_remaining_flashes = 0;
            return;
    }
    s_flash_phase = true;
    s_flash_timer_ms = FLASH_ON_TIME_MS;
    led_ui_set_blue(true);
}

void led_ui_tick(uint32_t delta_ms)
{
    if (s_remaining_flashes > 0) {
        if (delta_ms >= s_flash_timer_ms) {
            s_flash_timer_ms = 0;
            if (s_flash_phase) {
                /* Phase was ON -> turn OFF */
                led_ui_set_blue(false);
                s_flash_phase = false;
                s_flash_timer_ms = FLASH_OFF_TIME_MS;
            } else {
                /* Phase was OFF -> check remaining */
                s_remaining_flashes--;
                if (s_remaining_flashes > 0) {
                    led_ui_set_blue(true);
                    s_flash_phase = true;
                    s_flash_timer_ms = FLASH_ON_TIME_MS;
                }
            }
        } else {
            s_flash_timer_ms -= delta_ms;
        }
    }
}
