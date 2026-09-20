/**
 * @file power_mgr.h
 * @brief Power Management and Battery Voltage Monitoring
 * Target: STM32WL55 with MCP73831 Charger and AP2112K-3.3 LDO
 */

#ifndef POWER_MGR_H
#define POWER_MGR_H

#include <stdint.h>
#include <stdbool.h>
#include "../include/hardware_config.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BATTERY_CRITICAL = 0,   /* < 3.2V (Imminent shutdown) */
    BATTERY_LOW      = 1,   /* 3.2V - 3.4V (Warn user) */
    BATTERY_NOMINAL  = 2,   /* 3.4V - 3.8V */
    BATTERY_FULL     = 3    /* > 3.8V */
} battery_level_t;

typedef struct {
    uint16_t millivolts;    /**< Battery voltage in millivolts (e.g. 3700 mV) */
    battery_level_t level;  /**< Discrete state */
    bool is_charging;       /**< True if MCP73831 STAT pin is active */
} power_status_t;

/**
 * @brief Initialize power management and ADC peripherals
 */
void power_mgr_init(void);

/**
 * @brief Sample battery voltage and charging status
 * @param status Pointer to status struct to populate
 */
void power_mgr_update(power_status_t *status);

/**
 * @brief Enter low-power sleep mode until next interrupt or timer tick
 * @param sleep_duration_ms Sleep duration in milliseconds
 */
void power_mgr_sleep(uint32_t sleep_duration_ms);

#ifdef __cplusplus
}
#endif

#endif /* POWER_MGR_H */
