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

    def __repr__(self) -> str:
        s = self.opcode.name
        for op in self.operands:
            s += " " + repr(op)
        return s
    
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
        sys.stderr.write(
            colored("error:", "red", attrs=["bold"]) + " " +
            colored(message, attrs=["bold"]) + "\n")
        sys.stderr.write(f"{self.current_file}:{line_num}:{col_num +1}\n\n")
        sys.stderr.write(f"  {consumed_lines[-1]}{remaining_line}\n")
        sys.stderr.write(f"  {' '*col_num}^\n")
        sys.exit(1)

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
            return Instruction(Opcode.JRELI, [rs])

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
    
# parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("inputs", metavar="INPUT", nargs="*",
    help="input files to assemble")
args = parser.parse_args()

# parse the input file
parser = AssemblyParser()
for i in args.inputs:
    parser.parse_file(i)

print ("List of instructions that we parsed:\n")
print(parser.program)