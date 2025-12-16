/**
 * @file cpu.S
 * @brief Microcode Defines
 *
 * Various defines for the microcode.
 *
 * @author Samuel Fitzsimons (rainbain)
 * @date 2025
 */

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
