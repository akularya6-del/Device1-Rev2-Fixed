/**
 * @file led_ui.h
 * @brief Bi-Color Red/Blue LED UI Driver and Feedback State Machine
 */

#ifndef LED_UI_H
#define LED_UI_H

#include <stdint.h>
#include <stdbool.h>
#include "../include/hardware_config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    UI_STATE_IDLE = 0,
    UI_STATE_STREAMING,
    UI_STATE_ACK_FLASH,
    UI_STATE_BATTERY_LOW,
    UI_STATE_CHARGING
} ui_state_t;

/**
 * @brief Initialize GPIOs for Red and Blue LEDs (PB0 and PB1)
 */
void led_ui_init(void);

/**
 * @brief Set Red LED state
 */
void led_ui_set_red(bool on);

/**
 * @brief Set Blue LED state
 */
void led_ui_set_blue(bool on);

/**
 * @brief Trigger visual feedback flash for received Base Station command ('A', 'B', 'C', 'D')
 * @param cmd_code Command letter ('A'=1 flash, 'B'=2 flashes, 'C'=3 flashes, 'D'=4 flashes)
 */
void led_ui_indicate_cmd(uint8_t cmd_code);

/**
 * @brief Non-blocking UI tick handler called periodically from main loop
 * @param delta_ms Milliseconds elapsed since last tick
 */
void led_ui_tick(uint32_t delta_ms);

#ifdef __cplusplus
}
#endif

#endif /* LED_UI_H */
