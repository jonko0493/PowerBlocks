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

#pragma once

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef void (*dsp_handler_t)(void* user);

/**
 * @brief Resets the DSP and brings to a known state.
 * 
 * After this call, the DSP system will be in a known state
 * and ready to begin running code.
 * 
 * Feel free to call this multiple times if you ever need
 * to reset the DSP in a failure condition.
 */
extern void dsp_initialize();


/**
 * @brief Boots a program from IRAM
 * 
 * Boots a program for the DSP to run from IRAM.
 * 
 * This follows dsp_initialize, where the DSP is reset
 * to the internal ROM and ready for commands.
 * 
 * This will send it to IRAM to run a program after a quick
 * DMA session.
 * 
 * 
 * @param iram Instruction RAM data, 32 byte aligned
 * @param iram_size Size of the IRAM image to load
 * @param entry Entry point of program, offset into IRAM.
 */
extern void dsp_boot_program(const void* iram, size_t iram_size, uint16_t entry);

/**
 * @brief Gets a value from the DSP mailbox.
 * 
 * Reads 31 bits of data back from the DSP mailbox.
 * 
 * When the DSP writes data into the row register of the DSP
 * mailbox, bit 31 is set, and cleared after this function reads it.
 * 
 * @return Mailbox value
 */
extern uint32_t dsp_dsp_mailbox_get();

/**
 * @brief Sets a value to the DSP mailbox.
 * 
 * Sets 31 bits of data into the CPU mailbox.
 * 
 * Bit 31 is set with the CPU writes into it with this function,
 * and when the DSP reads the low register of the CPU mailbox
 * it is cleared.
 * 
 * @param value Value to put in mailbox
 */
extern void dsp_cpu_mailbox_set(uint32_t value);

/**
 * @brief Returns true if the DSP mailbox has mail.
 * 
 * It does this by checking bit 31 of the mailbox without clearing
 * the value.
 * 
 * Good to check if the DSP has sent mail.
 * 
 * @return True if the DSP mailbox has mail
 */
extern bool dsp_dsp_mailbox_full();

/**
 * @brief Returns true if the CPU mailbox has mail.
 * 
 * It does this by checking bit 31 of the mailbox without clearing
 * the value.
 * 
 * Good to check if the DSP has read our mail yet.
 * 
 * @return True if the CPU mailbox has mail
 */
extern bool dsp_cpu_mailbox_full();

/**
 * @brief Sets the handler on dsp interrupt.
 * 
 * Called when the DSP sets the IRQ register.
 * 
 * @param handler Handler to call on frame compilation
 * @param user User data to pass to the handler
*/
extern void dsp_set_callback(dsp_handler_t handler, void* user);


/**
 * @brief Initialize the audio interface
 * 
 * @param enable_32 If enabled, samples are played at 32 KS/s, otherwise 48 KS/s
 */
extern void dsp_ai_initialize(bool enable_32);

/**
 * @brief Sets the handler on frame compilation.
 * 
 * Called when a frame finishes player.
 * 
 * Do not call this when audio is playing as it could cause the
 * interrupt handler to read an invalid pointer.
 * 
 * @param handler Handler to call on frame compilation
 * @param user User data to pass to the handler
*/
extern void dsp_ai_set_callback(dsp_handler_t handler, void* user);

/**
 * @brief Play an audio frame
 * 
 * Begins streaming audio from RAM to the audio encoder.
 * 
 * If a callback is not set, audio will stop playing once the buffer is empty.
 * 
 * @param data Data, must be cache flushed and 32 byte aligned.
 * @param length Number of frames. That is the number of (L+R) sample pairs. Must be a multiple of 8
 */
extern void dsp_ai_play_frame(int16_t* samples, size_t length);

/**
 * @brief Stop and Start audio
 * 
 * This can be used to stop audio playback.
 * 
 * dsp_ai_play_sample automaticaly starts audio, and will stop it if no callback is set.
 * You can use this to pause and resume audio too
 * 
 * @param running If true, audio plays.
*/
extern void dsp_ai_set_running(bool running);