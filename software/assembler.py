#
import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from termcolor import colored
from typing import *


# The different kinds of operands we support
class OperandKind(Enum):
    Imm = auto()
    Reg = auto()
    RegPair = auto()

# An instruction operand, like a register oder an immediate value.
@dataclass
class Operand:
    kind: OperandKind
    value: Any 

    def __repr__(self) -> str:
        return f"{self.kind.name}:{self.value}"


# An instruction Opcode
class Opcode(Enum):
    # Actual instructions
    LDI = auto()
    MV = auto()
    JABSR =auto()
    JRELI = auto()
    JRELR = auto()
    NOP = auto()

    # Pseudo-instructions
    HALT = auto()

    # Assembler directives
    D_ORG = auto()
    


# An assembly instruction, represented by its opcode and list of operands
@dataclass
class Instruction:
    opcode: Opcode
    operands: List[Operand] = field(default_factory=list)
    address: Optional[int] = None
    encoding: Optional[int] = None

    def __repr__(self) -> str:
        s = self.opcode.name
        for op in self.operands:
            s += " " + repr(op)
        return s

# Report an error and exit with an error code
def error(message, *args):
    sys.stderr.write(
        colored("error:", "red", attrs=["bold"]) + " " +
        colored(message, attrs=["bold"]) + "\n")
    for arg in args:
        if arg is None:
            continue
        elif isinstance(arg, Instruction):
            pretty = AssemblyPrinter([arg]).print()
            sys.stderr.write(pretty)
        else:
            sys.stderr.write(arg + "\n")
    sys.exit(1)


# A parser that converts human-readable assembly text into a list of 'instruction' objects
@dataclass
class AssemblyParser:
    program: List[Instruction] = field(default_factory=list)
    # Abort with an error message.
    def error(self, message):
        consumed = len(self.current_contents) - len(self.current_input)
        consumed_lines = self.current_contents[0:consumed].split("\n")
        line_num = len(consumed_lines)
        col_num = len(consumed_lines[-1])
        remaining_line = self.current_input.split("\n")[0]
        
        error(
            message,
            f"{self.current_file}:{line_num}:{col_num +1}",
            "",
            f"  {consumed_lines[-1]}{remaining_line}",
            f"  {' '*col_num}^"
        )

    # Parse an entire assembly file.
    def parse_file(self, file: str):
        self.current_file = file
        with open(file, "r") as i:
            self.current_input = i.read()
            self.current_contents = self.current_input
        self.parse_program()
        self.current_file = None
        self.current_input = None
        self.current_contents = None

    def parse_program(self):
        self.skip()
        while len(self.current_input) > 0:
            inst = self.parse_instruction()
            print(inst)
            self.program.append(inst)
        
    # Parse instruction
    def parse_instruction(self) -> Instruction:
        # Actual instructions
        if self.consume_identifier("nop"):
            return Instruction(Opcode.NOP)
        
        if self.consume_identifier("ldi"):
            rd = self.parse_register()
            self.parse_regex(r',')
            imm = self.parse_immediate()
            return Instruction(Opcode.LDI, [rd, imm])
        
        if self.consume_identifier("mv"):
            rd = self.parse_register()
            self.parse_regex(r',')
            rs = self.parse_register()
            return Instruction(Opcode.MV, [rd, rs])
        
        if self.consume_identifier("jabsr"):
            rs16 = self.parse_register_pair()
            return Instruction(Opcode.JABSR, [rs16])

        if self.consume_identifier("jreli"):
            imm = self.parse_immediate()
            return Instruction(Opcode.JRELI, [imm])
        
        if self.consume_identifier("jrelr"):
            rs = self.parse_register()
            return Instruction(Opcode.JRELR, [rs])

        # Pseudo-instructions
        if self.consume_identifier("halt"):
            return Instruction(Opcode.HALT)

        # Directions
        if self.consume_identifier(r'\.org'):
            imm = self.parse_immediate()
            return Instruction(Opcode.D_ORG, [imm])
        
        self.error("unknown instruction")

    # Parse a register Operand like "r0".
    def parse_register(self) -> Operand:
        idx = int(self.parse_regex(r'r([0-6])\b', "expected a register")[1])
        return Operand(OperandKind.Reg, idx)

    # Parse a register pair, like r0r1
    def parse_register_pair(self) -> Operand:
        m =self.parse_regex(r'r([0-6])r([0-6])\b', "expected a 16bit register pair")
        lo = int(m[1])
        hi = int(m[2])
        if hi != lo + 1:
            self.error(f"Registers in 16bit must be conescutive {m[0]}")
        return Operand(OperandKind.RegPair, lo)
    # Parse an immediate, like 42 or 0xbeef or 0b10101111
    def parse_immediate(self) -> Operand:
        negative = False
        if m := self.consume_regex(r'[+-]', skip=False):
            negative = m[0] == '-'
        base = 10
        digits = r'[0-9_]+\b'
        if m := self.consume_regex(r'0[xob]', skip=False):
            if m[0] == "0x":
                base = 16
                digits = r'[0-9a-fA-F_]+\b'
            elif m[0] == "0o":
                base = 8
                digits = r'[0-7_]+\b'
            elif m[0] == "0b":
                base = 2
                digits = r'[01_]+\b'
            
        value = self.parse_regex(digits, f"expected base-{base} integer")
        value = int(value[0].replace("_", ""), base)
        if negative:
            value = -value
        return Operand(OperandKind.Imm, value)

    # Skip over whitespace and comments.
    def skip(self):
        while True:
            # skip whitespace
            if self.consume_regex(r'\s+', skip=False):
                continue
            # skip single line comment ( # or //)
            if self.consume_regex(r'(#|//).*[\n$]', skip=False):
                continue
            # skip multiline comment (/* ... +/)
            if self.consume_regex(r'(?s)/\*.*\*/', skip=False):
                continue
            break
    # if a regular expression matches at the current position in the input,
    # cosume the matched string and return the regex match object, if "skip" is 
    # set to true, also skip over whitespace following the match.
    def consume_regex(self, regex, skip: bool = True) -> Optional[re.Match]:
        if m := re.match(regex, self.current_input):
            self.current_input = self.current_input[len(m[0]):]
            if skip:
                self.skip()
            return m
        return None

    # Parse a regular expression. Print an error otherwise.
    def parse_regex(self, regex, error_message: Optional[str] = None) -> re.Match:
        if m := self.consume_regex(regex):
            return m
        self.error(error_message or f"expeted '{regex}'")

    # consume an identifier, like ldi or nop
    def consume_identifier(self, identifier: str) -> bool:
        if self.consume_regex(rf'{identifier}\b'):
            return True
        return False




# A printer that converts a list of "Instruction" objects into human-readable
# assembly text.
@dataclass
class AssemblyPrinter:
    program: List[Instruction]

    def print(self) -> str:
        self.emit_address = any(i.address is not None for i in self.program)
        self.emit_encoding = any(i.encoding is not None for i in self.program)
        self.output = ""
        for i in self.program:
            self.print_instruction(i)
            self.emit("\n")
        s = self.output
        self.output = None
        return s
    
    def print_instruction(self, inst: Instruction):
        # Print the address prefix
        if self.emit_address:
            address = "????"
            if inst.address is not None:
                address = f"{inst.address:04X}"
            self.emit(f"{address}:   ")

        # Print the instruction encoding
        if self.emit_encoding:
            encoding = "    "
            if inst.encoding is not None:
                encoding = f"{inst.encoding:04X}"
            self.emit(f"{encoding}  ")
        # Actual instructions   
        if inst.opcode == Opcode.NOP:
            self.print_opcode("nop")
            return
        
        if inst.opcode == Opcode.LDI:
            self.print_opcode("ldi ")
            self.print_operand(inst.operands[0])
            self.emit(", ")
            self.print_operand(inst.operands[1])
            return

        if inst.opcode == Opcode.MV:
            self.print_opcode("mv ")
            self.print_operand(inst.operands[0])
            self.emit(", ")
            self.print_operand(inst.operands[1])
            return

        if inst.opcode == Opcode.JABSR:
            self.print_opcode("jabsr ")
            self.print_operand(inst.operands[0])
            return

        if inst.opcode == Opcode.JRELI:
            self.print_opcode("jreli ")
            self.print_operand(inst.operands[0], hint_relative=True)
            if inst.address is not None:
                target_addr = inst.address + inst.operands[0].value
                self.emit(f"  # {target_addr:04X}")
            return
              
        if inst.opcode == Opcode.JRELR:
            self.print_opcode("jrelr ")
            self.print_operand(inst.operands[0])
            return
        
        # pseudo-instructions
        if inst.opcode == Opcode.HALT:
            self.print_opcode("halt ")
            return
        
        # directives
        if inst.opcode == Opcode.D_ORG:
            self.emit(".org ")
            self.print_operand(inst.operands[0], hint_addr=True)
            return

        self.emit(f"<{inst}")
        

    def print_opcode(self, text: str):
        self.emit(f"    {text:<7s}") # der Opcode wird mit mit whitspaces aufgefüllt, left alingned, also Opcode + " " bis es 7 chars sind
    
    def print_operand(self, operand: Operand, 
                      hint_relative: bool = False,
                      hint_addr=False
                      ):
        if operand.kind == OperandKind.Imm:
            if hint_addr:
                self.emit(f"0x{operand.value:04X}")
            elif operand.value >= 0 and hint_relative:
                self.emit(f"+{operand.value}")
            else:
                self.emit(f"{operand.value}")
        elif operand.kind == OperandKind.Reg:
            self.emit(f"r{operand.value}")
        elif operand.kind == OperandKind.RegPair:
            self.emit(f"r{operand.value}r{operand.value + 1}")


    def emit(self, text: str):
        self.output += text


# Utility to compute the exact address of instructions in the binary
@dataclass
class Layouter:
    current_address: int = 0

    def layout_program(self, program: List[Instruction]):
        for inst in program:
            self.layout_instruction(inst)

    def layout_instruction(self, inst: Instruction):
        if inst.opcode == Opcode.D_ORG:
            org_address = inst.operands[0].value
            if self.current_address > org_address:
                error(f"org directive address 0x{org_address:04X} behind current address 0x{self.current_address:04X}", inst)    
            self.current_address = org_address
            inst.address = org_address
            return
        
        inst.address = self.current_address
        self.current_address += 1

# An encoder that computes the binary encoding for every instruction in a program
class InstructionEncoder:
    def error(self, message: str):
        error(message, self.inst)

    def encode_program(self, program: List[Instruction]):
        for inst in program:
            self.inst = inst
            self.encoding = 0
            self.encode_instruction(inst)
            inst.encoding = self.encoding
            #sys.stdout.write(AssemblyPrinter([inst]).print())

    def encode_instruction(self, inst: Instruction):
        # Actual instructions
        if inst.opcode == Opcode.NOP:
            self.encode_bits(0, 16, 0x0000)
            return
        
        if inst.opcode == Opcode.LDI:
            self.encode_bits(0, 4, 0x8)
            self.encode_rd(inst.operands[0])
            self.encode_imm8(inst.operands[1])
            return
        
        if inst.opcode == Opcode.MV:
            self.encode_bits(0, 4, 0x0)
            self.encode_rd(inst.operands[0])
            self.encode_rs(inst.operands[1])
            return
        
        if inst.opcode == Opcode.JABSR:
            self.encode_bits(0, 8, 0x02)
            self.encode_rs16(inst.operands[0])
            return
        
        if inst.opcode == Opcode.JRELI:
            self.encode_bits(0, 8, 0x09)
            self.encode_simm8(inst.operands[0])
            return
        
        if inst.opcode == Opcode.JRELR:
            self.encode_bits(0, 8, 0x01)
            self.encode_rs(inst.operands[0])
            return
        
        if inst.opcode == Opcode.HALT:
            self.encode_bits(0, 16, 0x0009)
            return
        
        if inst.opcode == Opcode.D_ORG:
            self.encoding = None
            return

        self.error("unencodable instruction")
        
    # Store the "value" into the instruction bits from "offset" to "offset+length"
    def encode_bits(self, offset: int, length: int, value: int):
        assert(offset >= 0)
        assert(length >= 0)
        assert(offset + length <= 16)
        assert(value >= 0)
        assert(value < 2**length)
        mask = ((1 << length) -1) << offset
        self.encoding &= ~mask
        self.encoding |= value << offset
    
    # Encode a register operand in the "rd" field 
    def encode_rd(self, operand: Operand):
        if operand.kind != OperandKind.Reg or operand.value < 0 or operand.value > 6:
            self.error(f"expected rd register operand; got {operand}")
        self.encode_bits(4, 4, operand.value + 1)

    # Encode a register operand in the "rs" field 
    def encode_rs(self, operand: Operand):
        if operand.kind != OperandKind.Reg or operand.value < 0 or operand.value > 6:
            self.error(f"expected rs register operand; got {operand}")
        self.encode_bits(8, 4, operand.value + 1)

    # Encode a 16 bit register operand in the "rs16" field 
    def encode_rs16(self, operand: Operand):
        if operand.kind != OperandKind.RegPair or operand.value < 0 or operand.value > 5:
            self.error(f"expected rs16 register operand; got {operand}")
        self.encode_bits(8, 4, operand.value + 1)

    # encode an immediate operand in the 8 bit immediate field
    def encode_imm8(self, operand: Operand):
        self.check_imm(operand, -128, 256)
        self.encode_bits(8, 8, operand.value & 0xFF)
    
    # encode a signed immediate operand in the 8 bit immediate field
    def encode_simm8(self, operand: Operand):
        self.check_imm(operand, -128, 128)
        self.encode_bits(8, 8, operand.value & 0xFF)
    
    # Error if an operand is not an immediate, or the immediate is less, than "lower" or greater than of equal to "upper"
    def check_imm(self, operand: Operand, lower: int, upper: int):
        if operand.kind != OperandKind.Imm:
            self.error(f"expected immediate operand; got {operand}")
        value = operand.value
        if value < lower or value >= upper:
            self.error(f"immediate vlaue {value} is out of bounds, expected {lower} <= value < {upper}")
        


# parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("inputs", metavar="INPUT", nargs="*",
    help="input files to assemble")
args = parser.parse_args()

# parse the input file
parser = AssemblyParser()
for i in args.inputs:
    parser.parse_file(i)


# compute the addresses of each instruction
Layouter().layout_program(parser.program)

# Compute the binary encoding of each instruction
InstructionEncoder().encode_program(parser.program)

print ("List of instructions that we parsed:\n")
print(parser.program)

# Print the assembly
print("Assembler parsed Output: \n")
print(AssemblyPrinter(parser.program).print())

