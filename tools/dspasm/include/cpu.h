/**
 * @file cpu.S
 * @brief Microcode Defines For CPU
 *
 * Various defines for the microcode of the CPU.
 *
 * @author Samuel Fitzsimons (rainbain)
 * @date 2025
 */

/* -------------------Comparisons--------------------- */

#define CC_GE   0b0000   // Greater or Equal (Signed)
#define CC_LT   0b0001   // Less Than (Signed)
#define CC_GT   0b0010   // Greater Than (Signed)
#define CC_LE   0b0011   // Less or Equal (Signed)

#define CC_NZ   0b0100   // Not Zero
#define CC_Z    0b0101   // Zero

#define CC_NC   0b0110   // Not Carry
#define CC_C    0b0111   // Carry

#define CC_LT_U 0b1000   // Below (Unsigned)
#define CC_GT_U 0b1001   // Above (Unsigned)

#define CC_NLZ  0b1100   // Not Logical Zero
#define CC_LZ   0b1101   // Logical Zero

#define CC_V    0b1110   // Overflow
#define CC_AL   0b1111   // Always (Unconditional)

/* -------------------IXF--------------------- */

// All of these start at address 0xFF00
#define IXF_BASE 0xFF00

// ADPCM Coefficients
#define IXF_A1_0  0xA0
#define IXF_A2_0  0xA1
#define IXF_A1_1  0xA2
#define IXF_A2_1  0xA3
#define IXF_A1_2  0xA4
#define IXF_A2_2  0xA5
#define IXF_A1_3  0xA6
#define IXF_A2_3  0xA7
#define IXF_A1_4  0xA8
#define IXF_A2_4  0xA9
#define IXF_A1_5  0xAA
#define IXF_A2_5  0xAB
#define IXF_A1_6  0xAC
#define IXF_A2_6  0xAD
#define IXF_A1_7  0xAE
#define IXF_A2_7  0xAF

// DMA Interface
#define IXF_DSCR  0xC9 // Control
#define IXF_DSBL  0xCB // Block Length
#define IXF_DSPA  0xCD // DSP Memory Address
#define IXF_DSMAH 0xCE // CPU Memory Address H
#define IXF_DSMAL 0xCF // CPU MEmory Address L

// Accelerator
#define IXF_FORMAT     0xD1 // Sample Format
#define IXF_ACUNK1     0xD2 // Unknown, usually 3
#define IXF_ACDRAW     0xD3 // Raw data
#define IXF_ACSAH      0xD4 // Start Address H
#define IXF_ACSAL      0xD5 // Start Address L
#define IXF_ACEAH      0xD6 // End Address H
#define IXF_ACEAL      0xD7 // End Address L
#define IXF_ACCAH      0xD8 // Current Address H
#define IXF_ACCAL      0xD9 // Current Address L
#define IXF_PRED_SCALE 0xDA // ADPCM predictor and scale
#define IXF_YN1        0xDB // ADPCM Output History N-1
#define IXF_YN2        0xDC // ADPCM Output History N-2
#define IXF_ACDSAMP    0xDD // Processed Sample
#define IXF_GAIN       0xDE // Gain
#define IXF_ACIN       0xDF // Accelerator Input
#define IXF_AMDM       0xED // ARAM DMA Request Mask

// Interrupts
#define IXF_FIRQ       0xFB // IRQ Request

// Mailbox
#define IXF_DMDH       0xFC // DSP Mailbox High
#define IXF_DMDL       0xFD // DSP Mailbox Low
#define IXF_CMBH       0xFE // CPU Mailbox H
#define IXF_CMBL       0xFF // CPU Mailbox L