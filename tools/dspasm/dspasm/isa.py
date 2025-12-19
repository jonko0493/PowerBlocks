"""
DSP Microcode Assembler ISA

Defines the Instruction Set Architecture of the DSP.

Author: Samuel Fitzsimons (rainbain)
File: isa.py
Date: 2025
"""

from .utils import TokenConsumer, assembly_error, name_token

def copy_bits(input, bits, error_token, error):
    output = 0

    width = len(bits)
    mask = (1 << width) - 1
    input &= mask

    for i in range(len(bits)):
        dst_bit = bits[i]
        src_bit = len(bits) - i - 1

        output |= ((input >> src_bit) & 1) << dst_bit
        input &= ~(1 << src_bit)
    
    # Bits left over, thats bad.
    if input != 0:
        assembly_error(error_token, error)
    
    return output


class RegisterField:
    def __init__(self, name, bits, register_listing):
        self.name = name
        self.bits = bits
        self.register_listing = register_listing
    
    def evaluate(self, tokens, error_token, _):
        # We only expect 1 token, the register
        if len(tokens) != 1 or tokens[0].type != "REGISTER":
            assembly_error(error_token, f"Expected register")
        
        # Find the register
        name = tokens[0].value.lower()
        register_index = None
        i = 0
        for register in self.register_listing:
            if name in register:
                register_index = i

            i += 1
        
        if register_index == None:
            assembly_error(error_token, f"Register {name} is not a valid register to operand of {error_token.value}")
        
        return copy_bits(register_index, self.bits, error_token, f"Could not fit register index of {name_token(error_token)} into instruction, this is usually a bug, please report it,")

class ImmediateField:
    def __init__(self, name, bits, is_address = False):
        self.name = name
        self.bits = bits
        self.is_address = is_address
    
    def evaluate(self, tokens, error_token, program):
        # Evaluate expression
        if len(tokens) == 0:
            assembly_error(error_token, "Expected expression")
        
        value = program.evaluate_expression(tokens)

        if self.is_address:
            if value % 2 != 0:
                assembly_error(error_token, "Addresses must be 16 bit aligned")
            
            value //= 2

        return copy_bits(value, self.bits, error_token, f"Could not fit immediate into {name_token(error_token)}, make sure your immediate value is not too large")

class ExtendedOpcodeField:
    def __init__(self, bits):
        self.bits = bits
    
    def evaluate(self, value, error_token):
        return copy_bits(value, self.bits, error_token, f"Instruction {name_token(error_token)}, does not support this extension")

class OpcodeData:
    def __init__(self, program, opcode, endian="big"):
        self.program = program
        self.opcode = opcode
        self.endian = endian
        self.extended_opcode = None
    
    def consume(self, token, consumer: TokenConsumer, extended: bool):
        # Dont consume if no arguments
        if extended and len(self.opcode.fields) == 0:
            arguments = []
        else:
            arguments = consumer.consume_list(["COLON", "NEWLINE"])

        # Token for throwing errors
        self.error_token = token

        if len(arguments) != len(self.opcode.fields):
            assembly_error(token, f"Opcode {self.opcode.name} expects {len(self.opcode.fields)} fields, got {len(arguments)}")
        
        # Reorder arguments
        reordered = [arguments[i] for i in self.opcode.field_order]
        
        self.arguments = reordered
    
    def value(self):
        output = self.opcode.constant

        # Resolve each field
        for i in range(len(self.opcode.fields)):
            # Resolve expression
            output |= self.opcode.fields[i].evaluate(self.arguments[i], self.error_token, self.program)

        # Extended Opcode
        if self.extended_opcode:
            if not self.opcode.extended_opcode:
                assembly_error(self.error_token, f"Instruction {self.opcode.name} does not support extension")

            ext_output = self.extended_opcode.value()

            output |= self.opcode.extended_opcode.evaluate(ext_output, self.error_token)
        return output
    
    def serialize(self, pc):
        data = bytearray()

        if pc % 2 != 0:
            data.append(self.program.fill_pattern)
            pc += 1
        
        output = self.value()

        # Serialize output
        word_count = self.opcode.opcode_length // 2
        for i in range(word_count):
            shift = (word_count - (word_count - i)) * 16
            word = (output >> shift) & 0xFFFF

            data.extend(word.to_bytes(2, self.endian))

        return data

    def length(self, pc):
        # Alignment needed?
        if pc % 2 == 0:
            return self.opcode.opcode_length
        else:
            return self.opcode.opcode_length + 1
    
    def set_extension(self, opcode):
        self.extended_opcode = opcode

class Opcode:
    def __init__(self, name: str, fmt: str, registers = [], field_order = []):
        self.name = name
        self.registers = registers
        self.field_order = field_order
        self.extended_opcode = None

        # Remove spaces from format string
        fmt = fmt.replace(" ", "")

        # Instruction must be a multiple of 8 bits.
        if len(fmt) % 8 != 0:
            raise RuntimeError(f"Opcode {self.name} does not have a format thats a multiple of 16 bits.")
    
        # If is 8 bits, its an extended opcode
        self.word_bits = 16
        if len(fmt) == 8:
            self.word_bits = 8
        
        self.opcode_length = len(fmt) // 8

        # Decode format
        self.constant = 0
        self.fields = []

        field_type = None
        field_bits = []

        for i in range(len(fmt)):
            c = fmt[i]

            # It goes in order 15-0, then 15-0, and so on
            word = i // self.word_bits
            bit = (word * self.word_bits) + (self.word_bits - 1 - (i % self.word_bits))
            if c == '0' or c == '1':
                self.constant |= int(c) << bit
            else:
                # Ony accumulate field after checking 1 or 0
                # To allow for constants interested in a field

                # Field Changed?
                if field_type != c:
                    # Flush
                    if field_type != None:
                        self.add_field(field_type, field_bits)
                    
                    # Begin a new
                    field_type = c
                    field_bits = []

                field_bits.append(bit)
        
        # Flush remaining
        if field_type != None:
            self.add_field(field_type, field_bits)
        
        # Make sure no register listings remain
        if len(self.registers) != 0:
            raise RuntimeError(f"Opcode {self.name} has incorrect number of register listings for the fields provided.")
        
        # Make sure each field has an argument order
        if len(self.field_order) != len(self.fields):
            raise RuntimeError(f"Opcode {self.name} does not have a field order for each field.")
    
    def pop_register_listing(self):
        if len(self.registers) == 0:
            raise RuntimeError(f"Opcode {self.name} has incorrect number of register listings for the fields provided.")
        
        # Grab the first entry (not the last one hints the zero.)
        return self.registers.pop(0)
    
    def add_field(self, type, bits):
        field = None
        if type in ['d', 's', 't', 'r']:
            field = RegisterField(type, bits, self.pop_register_listing())
        elif type in ['i', 'c', 'm', 'h']:
            field = ImmediateField(type, bits)
        elif type in ['a']:
            field = ImmediateField(type, bits, is_address=True)
        elif type == "x":
            # These get special treatment, as their own unique field.
            self.extended_opcode = ExtendedOpcodeField(bits)
            return
        
        self.fields.append(field)
    
    def instantiate(self, program, token, consumer: TokenConsumer, extended: bool):
        op = OpcodeData(program, self)
        op.consume(token, consumer, extended)
        return op

OPCODE_LISTING = {}
EXT_OPCODE_LISTING = {}

REGISTER_ADDRESS = [
    ["$0", "$00", "$r00", "$ar0"],
    ["$1", "$01", "$r01", "$ar1"],
    ["$2", "$02", "$r02", "$ar2"],
    ["$3", "$03", "$r03", "$ar3"]
]

REGISTER_INDEXING = [
    ["$4", "$04", "$r04", "$ix0"],
    ["$5", "$05", "$r05", "$ix1"],
    ["$6", "$06", "$r06", "$ix2"],
    ["$7", "$07", "$r07", "$ix3"]
]

REGISTERS_SECONDARY_LOW = [
    ["$24", "$r18", "$ax0.l"],
    ["$25", "$r19", "$ax1.l"],
]

REGISTER_ACCUMULATOR_HIGH_1 = [
    ["$16", "$r10", "$ac0.h"],
    ["$17", "$r11", "$ac1.h"]
]

REGISTER_ACCUMULATOR_HIGH = [
    ["$26", "$r1A", "$ax0.h"],
    ["$27", "$r1B", "$ax1.h"],
]

REGISTER_ACCUMULATOR_SAH = REGISTERS_SECONDARY_LOW + REGISTER_ACCUMULATOR_HIGH

REGISTER_ACCUMULATOR_LOW = [
    ["$28", "$r1C", "$ac0.l"],
    ["$29", "$r1D", "$ac1.l"],
]

REGISTER_ACCUMULATOR_MID = [
    ["$30", "$r1E", "$ac0.m"],
    ["$31", "$r1F", "$ac1.m"],
]

REGISTER_ACCUMULATOR_LID = REGISTER_ACCUMULATOR_LOW + REGISTER_ACCUMULATOR_MID

REGISTERS_ACCUMULATOR = REGISTER_ACCUMULATOR_SAH + REGISTER_ACCUMULATOR_LID

REGISTERS = REGISTER_ADDRESS + REGISTER_INDEXING + [
    ["$8", "$08", "$r08", "$wr0"],
    ["$9", "$09", "$r09", "$wr1"],
    ["$10", "$r0A", "$wr2"],
    ["$11", "$r0B", "$wr3"],

    ["$12", "$r0C", "$st0"],
    ["$13", "$r0D", "$st1"],
    ["$14", "$r0E", "$st2"],
    ["$15", "$r0F", "$st3"],

] + REGISTER_ACCUMULATOR_HIGH_1 + [
    
    ["$18", "$r12", "$config"],
    ["$19", "$r13", "$sr"],

    ["$20", "$r14", "$prod.l"],
    ["$21", "$r15", "$prod.m1"],
    ["$22", "$r16", "$prod.h"],
    ["$23", "$r17", "$prod.m2"],
] + REGISTERS_ACCUMULATOR

REGISTER_FULL_ACCUMULATOR = [
    ["$ac0"],
    ["$ac1"]
]

REGISTER_SECONDARY_ACCUMULATOR = [
    ["$ax0"],
    ["$ax1"]
]

REGISTER_PARTS_AX0 = [
    ["$24", "$r18", "$ax0.l"],
    ["$26", "$r1A", "$ax0.h"],
]

REGISTER_PARTS_AX1 = [
    ["$25", "$r19", "$ax1.l"],
    ["$27", "$r1B", "$ax1.h"]
]



def add_opcode(opcode: Opcode):
    OPCODE_LISTING[opcode.name] = opcode

def add_ext_opcode(opcode: Opcode):
    EXT_OPCODE_LISTING[opcode.name] = opcode

add_opcode(Opcode("NOP",    "0000 0000 0000 0000"))
add_opcode(Opcode("DAR",    "0000 0000 0000 01dd", [REGISTER_ADDRESS], [0]))
add_opcode(Opcode("IAR",    "0000 0000 0000 10dd", [REGISTER_ADDRESS], [0]))
add_opcode(Opcode("SUBARN", "0000 0000 0000 11dd", [REGISTER_ADDRESS], [0]))
add_opcode(Opcode("ADDARN", "0000 0000 0001 ssdd", [REGISTER_INDEXING, REGISTER_ADDRESS], [1, 0]))
add_opcode(Opcode("HALT",   "0000 0000 0010 0001"))

add_opcode(Opcode("LOOP",   "0000 0000 010r rrrr", [REGISTERS], [0]))
add_opcode(Opcode("BLOOP",  "0000 0000 011r rrrr aaaa aaaa aaaa aaaa", [REGISTERS], [0, 1]))

add_opcode(Opcode("LRI",    "0000 0000 100d dddd iiii iiii iiii iiii", [REGISTERS], [0, 1]))
add_opcode(Opcode("LR",     "0000 0000 110d dddd mmmm mmmm mmmm mmmm", [REGISTERS], [0, 1]))
add_opcode(Opcode("SR",     "0000 0000 111s ssss mmmm mmmm mmmm mmmm", [REGISTERS], [1, 0]))

add_opcode(Opcode("IFCC",   "0000 0010 0111 cccc", [], [0]))
add_opcode(Opcode("JCC",    "0000 0010 1001 cccc aaaa aaaa aaaa aaaa", [], [1, 0]))
add_opcode(Opcode("CALLCC", "0000 0010 1011 cccc aaaa aaaa aaaa aaaa", [], [1, 0]))
add_opcode(Opcode("RETCC",  "0000 0010 1101 cccc", [], [0]))
add_opcode(Opcode("RTICC",  "0000 0010 1111 cccc", [], [0]))

add_opcode(Opcode("ADDI",   "0000 001d 0000 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("XORI",   "0000 001d 0010 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("ANDI",   "0000 001d 0100 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("ORI",    "0000 001d 0110 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("CMPI",   "0000 001d 1000 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("ANDF",   "0000 001d 1010 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("ANDCF",  "0000 001d 1100 0000 iiii iiii iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))

add_opcode(Opcode("LSRN",   "0000 0010 1100 1010"))
add_opcode(Opcode("ASRN",   "0000 0010 1100 1011"))

add_opcode(Opcode("ILRR",   "0000 001d 0001 00ss", [REGISTER_ACCUMULATOR_MID, REGISTER_ADDRESS], [0, 1]))
add_opcode(Opcode("ILRRD",  "0000 001d 0001 01ss", [REGISTER_ACCUMULATOR_MID, REGISTER_ADDRESS], [0, 1]))
add_opcode(Opcode("ILRRI",  "0000 001d 0001 10ss", [REGISTER_ACCUMULATOR_MID, REGISTER_ADDRESS], [0, 1]))
add_opcode(Opcode("ILRRN",  "0000 001d 0001 11ss", [REGISTER_ACCUMULATOR_MID, REGISTER_ADDRESS], [0, 1]))

add_opcode(Opcode("ADDIS",  "0000 010d iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("CMPIS",  "0000 011d iiii iiii", [REGISTER_ACCUMULATOR_MID], [0, 1]))
add_opcode(Opcode("LRIS",   "0000 1ddd iiii iiii", [REGISTERS_ACCUMULATOR], [0, 1]))

add_opcode(Opcode("LOOPI",  "0001 0000 iiii iiii", [], [0]))
add_opcode(Opcode("BLOOPI", "0001 0001 iiii iiii aaaa aaaa aaaa aaaa", [], [0, 1]))
add_opcode(Opcode("SBCLR",  "0001 0010 0000 0iii", [], [0]))
add_opcode(Opcode("SBSET",  "0001 0011 0000 0iii", [], [0]))

add_opcode(Opcode("LSL",    "0001 010r 00ii iiii", [REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("LSR",    "0001 010r 01ii iiii", [REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("ASL",    "0001 010r 10ii iiii", [REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("ASR",    "0001 010r 11ii iiii", [REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("SI",     "0001 0110 hhhh hhhh iiii iiii iiii iiii", [], [0, 1]))
add_opcode(Opcode("JRCC",   "0001 0111 rrr0 cccc", [REGISTERS], [0, 1]))
add_opcode(Opcode("CALLRCC","0001 0111 rrr1 cccc", [REGISTERS], [0, 1]))

add_opcode(Opcode("LRR",    "0001 1000 0ssd dddd", [REGISTER_ADDRESS, REGISTERS], [1, 0]))
add_opcode(Opcode("LRRD",   "0001 1000 1ssd dddd", [REGISTER_ADDRESS, REGISTERS], [1, 0]))
add_opcode(Opcode("LRRI",   "0001 1001 0ssd dddd", [REGISTER_ADDRESS, REGISTERS], [1, 0]))
add_opcode(Opcode("LRRN",   "0001 1001 1ssd dddd", [REGISTER_ADDRESS, REGISTERS], [1, 0]))
add_opcode(Opcode("SRR",    "0001 1010 0dds ssss", [REGISTER_ADDRESS, REGISTERS], [0, 1]))
add_opcode(Opcode("SRRD",   "0001 1010 1dds ssss", [REGISTER_ADDRESS, REGISTERS], [0, 1]))
add_opcode(Opcode("SRRI",   "0001 1011 0dds ssss", [REGISTER_ADDRESS, REGISTERS], [0, 1]))
add_opcode(Opcode("SRRN",   "0001 1011 1dds ssss", [REGISTER_ADDRESS, REGISTERS], [0, 1]))
add_opcode(Opcode("MRR",    "0001 11dd ddds ssss", [REGISTERS, REGISTERS], [0, 1]))

add_opcode(Opcode("LRS",    "0010 0ddd hhhh hhhh", [REGISTERS_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("SRSH",   "0010 100s hhhh hhhh", [REGISTER_ACCUMULATOR_HIGH_1], [1, 0]))
add_opcode(Opcode("SRS",    "0010 11ss hhhh hhhh", [REGISTER_ACCUMULATOR_LOW  + REGISTER_ACCUMULATOR_MID], [1, 0]))

add_opcode(Opcode("XORR",   "0011 00sd 0xxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_opcode(Opcode("ANDR",   "0011 01sd 0xxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_opcode(Opcode("ORR",    "0011 10sd 0xxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_opcode(Opcode("ANDC",   "0011 110d 0xxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))
add_opcode(Opcode("ORC",    "0011 111d 0xxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))

add_opcode(Opcode("XORC",   "0011 000d 1xxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))
add_opcode(Opcode("NOT",    "0011 001d 1xxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))
add_opcode(Opcode("LSRNRX", "0011 01sd 1xxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("ASRNRX", "0011 10sd 1xxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("LSRNR",  "0011 110d 1xxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("ASRNR",  "0011 111d 1xxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))

add_opcode(Opcode("ADDR",   "0100 0ssd xxxx xxxx", [REGISTERS_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("ADDAX",  "0100 10sd xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("ADD",    "0100 110d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("ADDP",   "0100 111d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))

add_opcode(Opcode("SUBR",   "0101 0ssd xxxx xxxx", [REGISTERS_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("SUBAX",  "0101 10sd xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("SUB",    "0101 110d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("SUBP",   "0101 111d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))

add_opcode(Opcode("MOVR",   "0110 0ssd xxxx xxxx", [REGISTERS_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("MOVAX",  "0110 10sd xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("MOV",    "0110 110d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MOVP",   "0110 111d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))

add_opcode(Opcode("ADDAXL", "0111 00sd xxxx xxxx", [REGISTERS_SECONDARY_LOW, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("INCM",   "0111 010d xxxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))
add_opcode(Opcode("INC",    "0111 011d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("DECM",   "0111 100d xxxx xxxx", [REGISTER_ACCUMULATOR_MID], [0]))
add_opcode(Opcode("DEC",    "0111 101d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("NEG",    "0111 110d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MOVNP",  "0111 111d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))

add_opcode(Opcode("NX",     "1000 x000 xxxx xxxx"))
add_opcode(Opcode("CLR",    "1000 r001 xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("CMP",    "1000 0010 xxxx xxxx"))
add_opcode(Opcode("MULAXH", "1000 0011 xxxx xxxx"))
add_opcode(Opcode("CLRP",   "1000 0100 xxxx xxxx"))
add_opcode(Opcode("TSTPROD","1000 0101 xxxx xxxx"))
add_opcode(Opcode("TSTAXH", "1000 011r xxxx xxxx", [REGISTER_ACCUMULATOR_HIGH], [0]))

add_opcode(Opcode("M2",     "1000 1010 xxxx xxxx"))
add_opcode(Opcode("M0",     "1000 1011 xxxx xxxx"))
add_opcode(Opcode("CLR15",  "1000 1100 xxxx xxxx"))
add_opcode(Opcode("SET15",  "1000 1101 xxxx xxxx"))
add_opcode(Opcode("SET16",  "1000 1110 xxxx xxxx"))
add_opcode(Opcode("SET40",  "1000 1111 xxxx xxxx"))

add_opcode(Opcode("MUL",    "1001 s000 xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR], [0]))
add_opcode(Opcode("ASR16",  "1001 r001 xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MULMVZ", "1001 s01r xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("MULAC",  "1001 s10r xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [0, 1]))
add_opcode(Opcode("MULMV",  "1001 s11r xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [0, 1]))

add_opcode(Opcode("MULX",   "101s t000 xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX0], [0, 1]))
add_opcode(Opcode("ABS",    "1010 d001 xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("TST",    "1011 r001 xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MULXMVZ","101s t01r xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))
add_opcode(Opcode("MULXAC", "101s t10r xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))
add_opcode(Opcode("MULXMV", "101s t11r xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))

add_opcode(Opcode("MULC",   "110s t000 xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH], [0, 1]))
add_opcode(Opcode("CMPAXH", "110r s001 xxxx xxxx", [REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("MULCMVZ","110s t01r xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))
add_opcode(Opcode("MULCAC", "110s t10r xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))
add_opcode(Opcode("MULCMV", "110s t11r xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH, REGISTER_FULL_ACCUMULATOR], [0, 1, 2]))

add_opcode(Opcode("MADDX",  "1110 00st xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1], [0, 1]))
add_opcode(Opcode("MSUBX",  "1110 01st xxxx xxxx", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1], [0, 1]))
add_opcode(Opcode("MADDC",  "1110 10st xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH], [0, 1]))
add_opcode(Opcode("MSUBC",  "1110 11st xxxx xxxx", [REGISTER_ACCUMULATOR_MID, REGISTER_ACCUMULATOR_HIGH], [0, 1]))

add_opcode(Opcode("LSL16",  "1111 000r xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MADD",   "1111 001s xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR], [0]))
add_opcode(Opcode("LSR16",  "1111 010r xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))
add_opcode(Opcode("MSUB",   "1111 011s xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR], [0]))
add_opcode(Opcode("ADDPAXZ","1111 10sd xxxx xxxx", [REGISTER_SECONDARY_ACCUMULATOR, REGISTER_FULL_ACCUMULATOR], [1, 0]))
add_opcode(Opcode("CLRL",   "1111 110r xxxx xxxx", [REGISTER_ACCUMULATOR_LOW], [0]))
add_opcode(Opcode("MOVPZ",  "1111 111d xxxx xxxx", [REGISTER_FULL_ACCUMULATOR], [0]))


add_ext_opcode(Opcode("NOP",     "0000 0000"))
add_ext_opcode(Opcode("DR",      "0000 01rr", [REGISTER_ADDRESS], [0]))
add_ext_opcode(Opcode("IR",      "0000 10rr", [REGISTER_ADDRESS], [0]))
add_ext_opcode(Opcode("NR",      "0000 11rr", [REGISTER_ADDRESS], [0]))
add_ext_opcode(Opcode("MV",      "0001 ddss", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_LID], [0, 1]))
add_ext_opcode(Opcode("S",       "001s s0dd", [REGISTER_ACCUMULATOR_LID, REGISTER_ADDRESS], [1, 0]))
add_ext_opcode(Opcode("SN",      "001s s1dd", [REGISTER_ACCUMULATOR_LID, REGISTER_ADDRESS], [1, 0]))
add_ext_opcode(Opcode("L",       "01dd d0ss", [REGISTERS_ACCUMULATOR, REGISTER_ADDRESS], [0, 1]))
add_ext_opcode(Opcode("LN",      "01dd d1ss", [REGISTERS_ACCUMULATOR, REGISTER_ADDRESS], [0, 1]))

add_ext_opcode(Opcode("LS",      "10dd 000s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [0, 1]))
add_ext_opcode(Opcode("SL",      "10dd 001s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_ext_opcode(Opcode("LSN",     "10dd 010s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [0, 1]))
add_ext_opcode(Opcode("SLN",     "10dd 011s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_ext_opcode(Opcode("LSM",     "10dd 100s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [0, 1]))
add_ext_opcode(Opcode("SLM",     "10dd 101s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [1, 0]))
add_ext_opcode(Opcode("LSNM",    "10dd 110s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [0, 1]))
add_ext_opcode(Opcode("SLNM",    "10dd 111s", [REGISTER_ACCUMULATOR_SAH, REGISTER_ACCUMULATOR_MID], [1, 0]))

add_ext_opcode(Opcode("LD",      "11dr 00ss", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_ADDRESS], [0, 1, 2]))
add_ext_opcode(Opcode("LDAX",    "11sr 0011", [REGISTER_ADDRESS, REGISTER_SECONDARY_ACCUMULATOR], [1, 0]))
add_ext_opcode(Opcode("LDN",     "11dr 01ss", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_ADDRESS], [0, 1, 2]))
add_ext_opcode(Opcode("LDAXN",   "11sr 0111", [REGISTER_ADDRESS, REGISTER_SECONDARY_ACCUMULATOR], [1, 0]))
add_ext_opcode(Opcode("LDM",     "11dr 10ss", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_ADDRESS], [0, 1, 2]))
add_ext_opcode(Opcode("LDAXM",   "11sr 1011", [REGISTER_ADDRESS, REGISTER_SECONDARY_ACCUMULATOR], [1, 0]))
add_ext_opcode(Opcode("LDNM",    "11dr 11ss", [REGISTER_PARTS_AX0, REGISTER_PARTS_AX1, REGISTER_ADDRESS], [0, 1, 2]))
add_ext_opcode(Opcode("LDAXNM",  "11sr 1111", [REGISTER_ADDRESS, REGISTER_SECONDARY_ACCUMULATOR], [1, 0]))