# ==============================================================================
# Device 1 Firmware Makefile
# Target: STM32WL55CCU6 (Dual-Core ARM Cortex-M4 @ 48MHz)
# Toolchain: Clang (Target: armv7em-none-eabi) + GNU ARM Linker & Objcopy
# ==============================================================================

CC      = clang
LD      = arm-none-eabi-ld
OBJCOPY = arm-none-eabi-objcopy
SIZE    = arm-none-eabi-size

TARGET  = Device1_Firmware

SRCS    = src/startup.c \
          src/main.c \
          codec/adpcm.c \
          audio/audio_i2s.c \
          radio/subghz_radio.c \
          power/power_mgr.c \
          ui/led_ui.c

INCS    = -Iinclude -Icodec -Iaudio -Iradio -Ipower -Iui

MCU     = -target armv7em-none-eabi -mcpu=cortex-m4 -mthumb -mfloat-abi=soft
CFLAGS  = $(MCU) $(INCS) -Os -Wall -Wextra -std=c11 -ffunction-sections -fdata-sections
LDFLAGS = -T stm32wl55ccu6.ld -Map=$(TARGET).map --gc-sections

OBJS    = $(SRCS:.c=.o)

all: $(TARGET).elf $(TARGET).bin $(TARGET).hex print_size

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET).elf: $(OBJS)
	$(LD) $(LDFLAGS) $(OBJS) -o $@

$(TARGET).bin: $(TARGET).elf
	$(OBJCOPY) -O binary $< $@

$(TARGET).hex: $(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

print_size: $(TARGET).elf
	@echo "=================================================="
	@echo "DEVICE 1 FIRMWARE MEMORY UTILIZATION SUMMARY"
	@echo "=================================================="
	$(SIZE) -B $(TARGET).elf

clean:
	rm -f $(OBJS) $(TARGET).elf $(TARGET).bin $(TARGET).hex $(TARGET).map

.PHONY: all clean print_size
