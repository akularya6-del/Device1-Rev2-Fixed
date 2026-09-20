/*
 * Linker script for STM32WL55CCU6 (256 KB Flash, 64 KB RAM)
 * Open Architecture Compact Wireless Audio Terminal
 */

ENTRY(Reset_Handler)

_estack = ORIGIN(RAM) + LENGTH(RAM); /* End of RAM = initial stack pointer */

MEMORY
{
    FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 256K
    RAM   (rw) : ORIGIN = 0x20000000, LENGTH = 64K
}

PHDRS
{
    text PT_LOAD FLAGS(5); /* Read + Execute (RX) */
    data PT_LOAD FLAGS(6); /* Read + Write (RW) */
}

SECTIONS
{
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        . = ALIGN(4);
    } >FLASH :text

    .text :
    {
        . = ALIGN(4);
        *(.text)
        *(.text*)
        *(.rodata)
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;
    } >FLASH :text

    _sidata = LOADADDR(.data);

    .data :
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data)
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } >RAM AT> FLASH :data

    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } >RAM :data

    /* Discard unused unwind tables */
    /DISCARD/ :
    {
        *(.ARM.exidx*)
        *(.note.gnu.build-id*)
    }
}
