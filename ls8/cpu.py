"""CPU functionality."""

import sys
from typing import List

class CPU:
    """Main CPU class."""
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

        self.commands = {
            0x00: self.no_op,
            0x01: self.halt, # !!!!!!!!
            0x11: self.return_from_subroutine,
            0x13: self.return_from_interrupt_handler,
            0x45: self.push,
            0x46: self.pop,
            0x47: self.print_number,
            0x48: self.print_alpha,
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
            0x82, # LDI  2 !!!!!!!
            0x83, # LD   2
            0x84, # ST   2
            0xA0: self.add,
            0xA1: self.sub,
            0xA2: self.mul,
            0xA3: self.div,
            0xA4: self.mod,
            0xA7: self.compare,
            0xA8: self.bit_and,
            0xAA: self.bit_or,
            0xAB: self.bit_xor,
            0xAC: self.bit_shift_left,
            0xAD: self.bit_shift_right,
        }

        self.alu_ops = {
            'ADD': lambda reg_a, reg_b: self.reg[reg_a] += self.reg[reb_b],
            'SUB': lambda reg_a, reg_b: self.reg[reg_a] -= self.reg[reb_b],
            'MUL': lambda reg_a, reg_b: self.reg[reg_a] *= self.reg[reb_b],
            'DIV': lambda reg_a, reg_b: self.reg[reg_a] /= self.reg[reb_b],
            'MOD': lambda reg_a, reg_b: self.reg[reg_a] %= self.reg[reb_b],
            # 'CMP': lambda reg_a, reg_b: self.reg[reg_a] += self.reg[reb_b],
            'AND': lambda reg_a, reg_b: self.reg[reg_a] &= self.reg[reb_b],
            'OR': lambda reg_a, reg_b: self.reg[reg_a] |= self.reg[reb_b],
            'XOR': lambda reg_a, reg_b: self.reg[reg_a] ^= self.reg[reb_b],
            'SHL': lambda reg_a, reg_b: self.reg[reg_a] <<= self.reg[reb_b],
            'SHR': lambda reg_a, reg_b: self.reg[reg_a] >>= self.reg[reb_b],
        }

    class HaltExcpetion(Exception):
        __init__(self, message: str):
            super().__init__(message)

    def get_one(self) -> int:
        pass

    def get_two(self) -> (int, int):
        pass

    def no_op(self):
        pass

    def halt(self):
        raise HaltExcpetion('halted')

    def return_from_subroutine(self):
        pass

    def return_from_interrupt_handler(self):
        pass

    def push(self):
        reg_a = self.get_one()
        pass

    def pop(self):
        reg_a = self.get_one()
        pass

    def print_number(self, register: int):
        reg_a = self.get_one()
        print(self.reg[reg_a])

    def print_alpha(self, register: int):
        reg_a = self.get_one()
        print(chr(self.reg[reg_a]))

    def add(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def sub(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def mul(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def div(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def mod(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def compare(self):
        reg_a, reg_b = self.get_two()
        pass

    def bit_and(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def bit_or(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def bit_xor(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def bit_shift_left(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

    def bit_shift_right(self):
        reg_a, reg_b = self.get_two()
        self.alu('ADD', reg_a, reg_b)

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
        try:
            self.alu_ops[op]()
        except KeyError
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

    def run_next_command(self) -> bool:
        self.mar += 1
        self.pc = self.mar
        try:
            self.ir = self.ram_read(self.pc)
            self.commands[self.ir]()
        except IndexError:
            return False
        except KeyError:
            return False
        return True

    def run(self):
        """Run the CPU."""
        try:
            while self.run_next_command():
                pass
        except HaltExcpetion:
            pass
