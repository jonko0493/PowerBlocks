/**
 * @file dsp.h
 * @brief Control the external DSP processor.
 *
 * Control the external DSP processor.
 *
 * @author Samuel Fitzsimons (rainbain)
 * @date 2025
 * @license MIT (see LICENSE file)
 */
#include "dsp.h"

#include "system/exceptions.h"
#include "system/system.h"

#include "utils/log.h"

#include <stdint.h>
#include <stdio.h>

static const char* TAG = "DSP";

#define DSP_ERROR_LOGGING
#define DSP_INFO_LOGGING
#define DSP_DEBUG_LOGGING

#ifdef DSP_ERROR_LOGGING
#define DSP_LOG_ERROR(fmt, ...) DSP_ERROR(TAG, fmt, ##__VA_ARGS__)
#else
#define DSP_LOG_ERROR(fmt, ...)
#endif 

#ifdef DSP_INFO_LOGGING
#define DSP_LOG_INFO(fmt, ...) LOG_INFO(TAG, fmt, ##__VA_ARGS__)
#else
#define DSP_LOG_INFO(fmt, ...)
#endif 

#ifdef DSP_DEBUG_LOGGING
#define DSP_LOG_DEBUG(fmt, ...) LOG_DEBUG(TAG, fmt, ##__VA_ARGS__)
#else
#define DSP_LOG_DEBUG(fmt, ...)
#endif

// In accordance to https://wiibrew.org/wiki/Hardware/DSP
#define DSP_MAILBOX_OUT_H      (*(volatile uint16_t*)0xCC005000)
#define DSP_MAILBOX_OUT_L      (*(volatile uint16_t*)0xCC005002)
#define DSP_MAILBOX_IN_H       (*(volatile uint16_t*)0xCC005004)
#define DSP_MAILBOX_IN_L       (*(volatile uint16_t*)0xCC005006)
#define DSP_CONTROL            (*(volatile uint16_t*)0xCC00500A)
#define DSP_AR_SIZE            (*(volatile uint16_t*)0xCC005012)
#define DSP_AR_MODE            (*(volatile uint16_t*)0xCC005016)
#define DSP_AR_REFRESH         (*(volatile uint16_t*)0xCC00501A)
#define DSP_AR_DMA_MMADDR_H    (*(volatile uint16_t*)0xCC005020)
#define DSP_AR_DMA_MMADDR_L    (*(volatile uint16_t*)0xCC005022)
#define DSP_AR_DMA_ARADDR_H    (*(volatile uint16_t*)0xCC005024)
#define DSP_AR_DMA_ARADDR_L    (*(volatile uint16_t*)0xCC005026)
#define DSP_AR_DMA_SIZE_H      (*(volatile uint16_t*)0xCC005028)
#define DSP_AR_DMA_SIZE_L      (*(volatile uint16_t*)0xCC00502A)
#define DSP_DMA_START_ADDR_H   (*(volatile uint16_t*)0xCC005030) // Audio Encoder DMA Address
#define DSP_DMA_START_ADDR_L   (*(volatile uint16_t*)0xCC005032) // Audio Encoder DMA Address
#define DSP_DMA_CONTROL_LENGTH (*(volatile uint16_t*)0xCC005036) // Audio encoder control and samples
#define DSP_DMA_BYTES_LEFT     (*(volatile uint16_t*)0xCC00503A) // How many bytes left

// Separate page, https://wiibrew.org/wiki/Hardware/Audio_Interface
// NOTE: This has a different address on gamecube.
// Seems likely many of these registers are not implemented on the
// wii. Quite possibly just DSP_AI_CONTROL and DSP_AI_AISCNT?
#define DSP_AI_CONTROL         (*(volatile uint16_t*)0xCD006C00)
#define DSP_AI_VOLUME          (*(volatile uint16_t*)0xCD006C04)
#define DSP_AI_AISCNT          (*(volatile uint32_t*)0xCD006C08)
#define DSP_AI_AIIT            (*(volatile uint32_t*)0xCD006C0C)

// DSP_CONTROL_EARLY_INIT is a bit odd and not fully understood

#define DSP_CONTROL_EARLY_INIT (1<<11) 
#define DSP_CONTROL_DMASTAT    (1<<10) // DSP initiated transfer in progress
#define DSP_CONTROL_ARDMASTAT  (1<<9)  // ARAM DMA transfer in progress
#define DSP_CONTROL_DSPINTMSK  (1<<8)  // Enable DSP Interrupts
#define DSP_CONTROL_DSPINT     (1<<7)  // DSP Interrupt active, write 1 to clear
#define DSP_CONTROL_ARINTMSK   (1<<6)  // ARAM DMA Interrupt Mask
#define DSP_CONTROL_ARINT      (1<<5)  // ARAM DMA Interrupt, write 1 to clear
#define DSP_CONTROL_AIDINTMSK  (1<<4)  // Audio Interface Interrupt Mask
#define DSP_CONTROL_AIDINT     (1<<3)  // Audio Interface Interrupt, write 1 to clear
#define DSP_CONTROL_HALT       (1<<2)  // Halts the DSP
#define DSP_CONTROL_PIINT      (1<<1)  // Assert DSP Interrupt
#define DSP_CONTROL_HARD_RESET (1<<0)  // Write 1 to reset the DSP, auto clears to 0. Wait for that

#define DSP_AI_CONTROL_RATE       (1<<6) // If set, goes to 32 KS/s and not 48 KS/s
#define DSP_AI_CONTROL_SCRESET    (1<<5) // Reset the audio sample counter
#define DSP_AI_CONTROL_INTVALID   (1<<4) // Interrupt asserted, independent of interrupt mask
#define DSP_AI_CONTROL_INT        (1<<3) // Audio interface interrupt, write 1 to clear
#define DSP_AI_CONTROL_INTMSK     (1<<2) // Audio interface interrupt mask
#define DSP_AI_CONTROL_AFR        (1<<1) // Match the value of RATE,  should be set only when PSTAT is cleared
#define DSP_AI_CONTROL_PSTAT      (1<<0) // Play status, enable playback by writing 1. Otherwise its paused.

static struct {
    dsp_handler_t handler;
    void* handler_user;

    dsp_handler_t ai_handler;
    void* ai_handler_user;
} dsp_state;

static void dsp_ai_irq();

static void dsp_irq() {
    uint16_t cause = DSP_CONTROL;

    if(cause & DSP_CONTROL_DSPINT) {
        if(dsp_state.handler)
            dsp_state.handler(dsp_state.handler_user);
    }

    if(cause & DSP_CONTROL_ARINT) {

    }

    if(cause & DSP_CONTROL_AIDINT) {
        dsp_ai_irq();
    }

    // Clear all interrupts
    DSP_CONTROL |= DSP_CONTROL_DSPINT | DSP_CONTROL_ARINT | DSP_CONTROL_AIDINT;

}

void dsp_initialize() {
    // Release reset
    DSP_CONTROL |= DSP_CONTROL_HARD_RESET | DSP_CONTROL_HALT;
    while(DSP_CONTROL & DSP_CONTROL_HARD_RESET);

    dsp_state.handler = NULL;

    // Enable interrupts
    DSP_CONTROL |= DSP_CONTROL_DSPINTMSK | DSP_CONTROL_AIDINTMSK;

    // Go CPU go
    DSP_CONTROL &= ~DSP_CONTROL_HALT;

    exceptions_install_irq(dsp_irq, EXCEPTION_IRQ_TYPE_DSP);

    DSP_LOG_INFO("Successfully Initialized");
}

// Waits for the ROM to set its mailbox.
// Used for early init. I would not recommend such a polling function for later things.
static void dsp_rom_mailbox_send_and_wait(uint32_t value) {
    // Wait for mail to clear.
    while(dsp_cpu_mailbox_full());
    
    dsp_cpu_mailbox_set(value);
}

void dsp_boot_program(const void* iram, size_t iram_size, uint16_t entry) {
    // Very specific sequence from YAGCD to cause the DSP to load our program

    uint32_t iram_address = SYSTEM_MEM_PHYSICAL(iram);

    // Load Source IRAM address
    dsp_rom_mailbox_send_and_wait(0x80F3A001);
    dsp_rom_mailbox_send_and_wait(iram_address);

    // IRAM start address, lets say 0
    dsp_rom_mailbox_send_and_wait(0x80F3C002);
    dsp_rom_mailbox_send_and_wait(0);

    // Download Size
    dsp_rom_mailbox_send_and_wait(0x80F3A002);
    dsp_rom_mailbox_send_and_wait(iram_size);

    // Supposedly a ARAM start address? Lets put 0
    dsp_rom_mailbox_send_and_wait(0x80F3B002);
    dsp_rom_mailbox_send_and_wait(0);

    // Entry point
    dsp_rom_mailbox_send_and_wait(0x80F3D001);
    dsp_rom_mailbox_send_and_wait(entry);

    DSP_LOG_INFO("All loaded");
}

uint32_t dsp_dsp_mailbox_get() {
    return ((uint32_t)DSP_MAILBOX_IN_H << 16) | (uint32_t)DSP_MAILBOX_IN_L;
}

void dsp_cpu_mailbox_set(uint32_t value) {
    DSP_MAILBOX_OUT_H = value >> 16;
    DSP_MAILBOX_OUT_L = value & 0xFFFF;
}

bool dsp_dsp_mailbox_full() {
    return (DSP_MAILBOX_IN_H & 0x8000) > 0;
}

bool dsp_cpu_mailbox_full() {
    return (DSP_MAILBOX_OUT_H & 0x8000) > 0;
}

void dsp_set_callback(dsp_handler_t handler, void* user) {
    dsp_state.handler = handler;
    dsp_state.handler_user = user;
}

/* -------------------Audio Interface--------------------- */

static void dsp_ai_irq() {
    // Is there a handler?
    if(dsp_state.ai_handler) {
        // Then let them cook
        dsp_state.ai_handler(dsp_state.ai_handler_user);
    } else {
        // Otherwise, stop playback.
        dsp_ai_set_running(false);
    }

    // Acknowledge the interrupt
    DSP_CONTROL |= DSP_CONTROL_AIDINT;
}

void dsp_ai_initialize(bool enable_32) {
    // Turn off, clear out everything
    DSP_AI_CONTROL = 0;

    dsp_state.ai_handler = NULL;

    // Set sample rate
    if(enable_32) {
        DSP_AI_CONTROL |= DSP_AI_CONTROL_RATE | DSP_AI_CONTROL_AFR;
    } else {
        DSP_AI_CONTROL &= ~(DSP_AI_CONTROL_RATE | DSP_AI_CONTROL_AFR);
    }

    // Begin sending data to encoder.
    DSP_AI_CONTROL |= DSP_AI_CONTROL_PSTAT;
}

void dsp_ai_set_callback(dsp_handler_t handler, void* user) {
    dsp_state.ai_handler = handler;
    dsp_state.ai_handler_user = user;
}

void dsp_ai_play_frame(int16_t* samples, size_t length) {
    // Physical address
    uint32_t physical = SYSTEM_MEM_PHYSICAL(samples);

    DSP_DMA_START_ADDR_H = physical >> 16;
    DSP_DMA_START_ADDR_L = physical & 0xFFFF;
    
    // GO, size = frames * 2 channels * 2 bytes per sample
    DSP_DMA_CONTROL_LENGTH = (length * sizeof(int16_t) * 2 / 32) | 0x8000;
}

void dsp_ai_set_running(bool running) {
    if(running) {
        DSP_DMA_CONTROL_LENGTH |= 0x8000;
    } else {
        DSP_DMA_CONTROL_LENGTH &= ~0x8000;
    }
}