"""
DSP Microcode Assembler Verification Tool

Used to verify the output of the tool after modification.

Author: Samuel Fitzsimons (rainbain)
File: dspasm_verify.py
Date: 2025
"""

import argparse
import sys
import os
from pathlib import Path

from dspasm.preprocessor import Preprocessor
from dspasm.parser import Parser
from dspasm.utils import dump_tokens_to_file

def verify(source, binary, symbols):
    if len(source) != len(binary):
        print(f"Verification Error. Source binary has size {len(source)} bytes, while the one were verifying against is {len(binary)}")
        return False

    passed = True
    
    for i in range(len(source)):
        if source[i] != binary[i]:
            print(f"Mismatch found at PC {hex(i)}, expected {hex(binary[i])}, got {hex(source[i])}")
            
            token = None
            for j in range(1, len(symbols)):
                pc, symbol = symbols[j]

                if pc > i:
                    _, token = symbols[j-1]
                    break
            
            if token:
                print(f"  {token}")

            passed = False

    return passed

def main():
    parser = argparse.ArgumentParser(description="PowerBlocks DSP Microcode Binary Verifier")
    parser.add_argument("source", type=Path)
    parser.add_argument("binary", type=Path)
    parser.add_argument("-t", "--tokens", type=Path, help="Dump tokens after preprocessor to file for debugging.")
    parser.add_argument("-bt", "--backtrace", action="store_true")
    
    args = parser.parse_args()

    input_source = args.source

    # Read binary we want to verify
    with open(args.binary, mode='rb') as file:
        input_binary = file.read()

    try:
        preprocessor = Preprocessor()

        # Recursive include
        tokens = preprocessor.recursive_include(input_source)

        # Take on all the macros
        tokens = preprocessor.gather(tokens)

        # Do not allow circular definitions
        preprocessor.check_circular_definitions()

        # Evaluate
        tokens = preprocessor.run(tokens)
    except Exception as e:
        # If backtrace, send this off to the top
        if args.backtrace:
            raise e

        print(f"{os.path.basename(input_source)}: Preprocessor Failed")
        print(f"\t{e}")
        sys.exit(1)
    
    # Dump them if asked
    if args.tokens:
        dump_tokens_to_file(tokens, args.tokens)

    try:
        # Generate program
        parser = Parser()
        program = parser.run(tokens)
    except Exception as e:
        # If backtrace, send this off to the top
        if args.backtrace:
            raise e

        print(f"{os.path.basename(input_source)}: Parser Failed")
        print(f"\t{e}")
        sys.exit(1)
    
    try:
        # Create bytecode
        bytecode, symbol_listing = program.generate_bytecode()
    except Exception as e:
        # If backtrace, send this off to the top
        if args.backtrace:
            raise e

        print(f"{os.path.basename(input_source)}: Bytecode Generation Failed")
        print(f"\t{e}")
        sys.exit(1)

    result = verify(bytecode, input_binary, symbol_listing)

    if result:
        print("Verification Passed")
    else:
        print("Verification Failed")

if __name__ == "__main__":
    main()