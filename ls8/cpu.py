"""CPU functionality."""

import sys
from typing import List

class CPU:
    """Main CPU class."""
    commands = {
        0x00, # NOP  0
        0x01, # HLT  0
        0x11, # RET  0
        0x13, # IRET 0
        0x45, # PUSH 1
        0x46, # POP  1
        0x47, # PRN  1
        0x48, # PRA  1
        0x50, # CALL 1
        0x52, # INT  1
        0x54, # JMP  1
        0x55, # JEQ  1
        0x56, # JNE  1
        0x57, # JGT  1
        0x58, # JLT  1
        0x59, # JLE  1
        0x5A, # JGE  1
        0x65, # INC  1
        0x66, # DEC  1
        0x69, # NOT  1
        0x82, # LDI  2
        0x83, # LD   2
        0x84, # ST   2
        0xA0, # ADD  2
        0xA1, # SUB  2
        0xA2, # MUL  2
        0xA3, # DIV  2
        0xA4, # MOD  2
        0xA7, # CMP  2
        0xA8, # AND  1
        0xAA, # OR   2
        0xAB, # XOR  2
        0xAC, # SHL  2
        0xAD, # SHR  2
    }

    def __init__(self):
        """Construct a new CPU."""
        self.ram: List[int] = [0] * 256
        self.reg: List[int] = [0] * 8
        # reg[5] IM or interrupt mask
        # reg[6] IS or interrupt status
        # reg[7] SP or stack pointer
        self.pc: int = 0 # program counter address
        self.ir: int = 0 # instruction register data
        self.mar: int = 0 # memory address register
        self.mdr: int = 0 # memory data register
        self.fl: int = 0 # flags bitfield 00000LGE

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def ram_read(self, address: int) -> int:
        return self.ram[address]

    def ram_write(self, value: int, address: int):
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + b'x1'),
            self.ram_read(self.pc + b'x2'),
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def set_next_state(self) -> bool:
        self.pc += 1
        try:
            self.ir = self.ram_read(self.pc)
            
        except IndexError:
            return False

    def run(self):
        """Run the CPU."""
        while self.set_next_state():
            pass
