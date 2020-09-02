"""CPU functionality."""

import sys
from typing import List

class CPU:
    """Main CPU class."""

    LESS_THAN_BIT_MASK    = 0b00000100
    GREATER_THAN_BIT_MASK = 0b00000010
    EQUAL_TO_BIT_MASK     = 0b00000001

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
            0x01: self.halt,
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
            0x65: lambda: self.alu('INC', self.get_next())
            0x66: lambda: self.alu('DEC', self.get_next()),
            0x69: lambda: self.alu('NOT', self.get_next()),
            0x82: self.ldi,
            0x83: self.ld,
            0x84: self.store,
            0xA0: lambda: self.alu('ADD', self.get_next(), self.get_next()),
            0xA1: lambda: self.alu('SUB', self.get_next(), self.get_next()),
            0xA2: lambda: self.alu('MUL', self.get_next(), self.get_next()),
            0xA3: lambda: self.alu('DIV', self.get_next(), self.get_next()),
            0xA4: lambda: self.alu('MOD', self.get_next(), self.get_next()),
            0xA7: lambda: self.alu('CMP', self.get_next(), self.get_next()),
            0xA8: lambda: self.alu('AND', self.get_next(), self.get_next()),
            0xAA: lambda: self.alu('OR', self.get_next(), self.get_next()),
            0xAB: lambda: self.alu('XOR', self.get_next(), self.get_next()),
            0xAC: lambda: self.alu('SHL', self.get_next(), self.get_next()),
            0xAD: lambda: self.alu('SHR', self.get_next(), self.get_next()),
        }

        self.alu_ops = {
            'INC': lambda address, _=None: self.reg[address] -= 1,
            'DEC': lambda address, _=None: self.reg[address] += 1,
            'NOT': lambda address, _=None: ~self.reg[address],
            'ADD': lambda address_a, address_b: self.reg[address_a] += self.reg[address_b],
            'SUB': lambda address_a, address_b: self.reg[address_a] -= self.reg[address_b],
            'MUL': lambda address_a, address_b: self.reg[address_a] *= self.reg[address_b],
            'DIV': lambda address_a, address_b: self.reg[address_a] /= self.reg[address_b],
            'MOD': lambda address_a, address_b: self.reg[address_a] %= self.reg[address_b],
            'CMP': lambda address_a, address_b: self.compare(address_a, address_b),
            'AND': lambda address_a, address_b: self.reg[address_a] &= self.reg[address_b],
            'OR': lambda address_a, address_b: self.reg[address_a] |= self.reg[address_b],
            'XOR': lambda address_a, address_b: self.reg[address_a] ^= self.reg[address_b],
            'SHL': lambda address_a, address_b: self.reg[address_a] << self.reg[address_b],
            'SHR': lambda address_a, address_b: self.reg[address_a] >> self.reg[address_b],
        }

    class HaltExcpetion(Exception):
        __init__(self, message: str):
            super().__init__(message)

    def get_next(self) -> int:
        self.mar += 1
        return self.ram_read(self.mar)

    def no_op(self):
        return 0
        pass

    def halt(self):
        raise HaltExcpetion('halted')

    def return_from_subroutine(self):
        return 0
        pass

    def return_from_interrupt_handler(self):
        return 0
        pass

    def push(self):
        address = self.get_next()
        pass

    def pop(self):
        address = self.get_next()
        pass

    def print_number(self, register: int):
        print(self.reg[self.get_next()])

    def print_alpha(self, register: int):
        print(chr(self.reg[self.get_next()]))

    def ldi(self):
        self.reg[self.get_next()] = self.get_next() # work on this? maybe incriment other things as well, maybe that's handled in get_two

    def ld(self):
        self.reg[self.get_next()] = self.reg[self.get_next()]

    def store(self):
        pass

    def compare(self, address_a, address_b):
        if self.reg[address_a] == self.reg[address_b]:
            self.fl = CPU.EQUAL_TO_BIT_MASK
        elif self.reg[address_a] < self.reg[address_b]:
            self.fl = CPU.LESS_THAN_BIT_MASK
        else:
            self.fl = CPU.GREATER_THAN_BIT_MASK
        pass

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
            self.alu_ops[op](reg_a, reg_b)
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
            steps_taken = self.commands[self.ir]()
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
