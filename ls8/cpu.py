"""CPU functionality."""

import sys
from typing import Dict, List, Optional

class CPU:
    """Main CPU class."""

    LESS_THAN_BIT_MASK = 0b00000100
    GREATER_THAN_BIT_MASK = 0b00000010
    EQUAL_TO_BIT_MASK = 0b00000001

    def __init__(self):
        """Construct a new CPU."""
        self.ram: List[int] = [0] * 256
        self.reg: List[int] = [0] * 8
        # reg[5] IM or interrupt mask
        # reg[6] IS or interrupt status
        # reg[7] SP or stack pointer
        self.mar: int = 0 # memory address register
        self.mdr: int = self.ram_read(self.mar) # memory data register
        self.pc: int = self.mar # program counter address
        self.ir: int = self.ram_read(self.pc) # instruction register data
        self.fl: int = 0b00000000

        self.commands: Dict[int, callable] = {
            0x00: self.no_op,
            0x01: self.halt,
            0x11: self.return_from_subroutine,
            0x13: self.return_from_interrupt_handler,
            0x45: self.push,
            0x46: self.pop,
            0x47: self.print_number,
            0x48: self.print_alpha,
            0x50: lambda _: _, # CALL 1 finish
            0x52: lambda _: _, # INT  1 finish
            0x54: self.jump,
            0x55: self.jump_if_equal_to,
            0x56: self.jump_if_not_equal_to,
            0x57: self.jump_if_greater_than,
            0x58: self.jump_if_less_than,
            0x59: self.jump_if_less_than_or_equal_to,
            0x5A: self.jump_if_greater_than_or_equal_to,
            0x65: lambda: self.alu('INC', self.get_next()),
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

        self.alu_ops: Dict[str, callable] = {
            'INC': self.increment,
            'DEC': self.decrement,
            'NOT': self.alu_not,
            'ADD': self.add,
            'SUB': self.subtract,
            'MUL': self.multiply,
            'DIV': self.divide,
            'MOD': self.mod,
            'CMP': self.compare,
            'AND': self.bit_and,
            'OR':  self.bit_or,
            'XOR': self.bit_xor,
            'SHL': self.shift_left,
            'SHR': self.shift_right,
        }

    class HaltExcpetion(Exception):
        def __init__(self, message: str):
            super().__init__(message)

    def get_next(self) -> int:
        self.mar += 1
        self.mdr = self.ram_read(self.mar)
        return self.mdr

    def no_op(self):
        pass

    def halt(self):
        raise CPU.HaltExcpetion('halted')

    def return_from_subroutine(self):
        pass

    def return_from_interrupt_handler(self):
        pass

    def push(self):
        pass

    def pop(self):
        pass

    def print_number(self):
        print(self.reg[self.get_next()])

    def print_alpha(self):
        print(chr(self.reg[self.get_next()]))


    def increment(self, address: int, _):
        self.reg[address] = (self.reg[address] + 1) & 0xFF

    def decrement(self, address: int, _):
        self.reg[address] = (self.reg[address] - 1) & 0xFF

    def alu_not(self, address: int, _):
        self.reg[address] = ~self.reg[address]

    def add(self, address_a: int, address_b: int):
        self.reg[address_a] = (self.reg[address_a] + self.reg[address_b]) & 0xFF

    def subtract(self, address_a: int, address_b: int):
        self.reg[address_a] = (self.reg[address_a] - self.reg[address_b]) & 0xFF

    def multiply(self, address_a: int, address_b: int):
        self.reg[address_a] = (self.reg[address_a] * self.reg[address_b]) & 0xFF

    def divide(self, address_a: int, address_b: int):
        self.reg[address_a] //= self.reg[address_b]

    def mod(self, address_a: int, address_b: int):
        self.reg[address_a] %= self.reg[address_b]

    def compare(self, address_a: int, address_b: int):
        if self.reg[address_a] == self.reg[address_b]:
            self.fl = CPU.EQUAL_TO_BIT_MASK
        elif self.reg[address_a] < self.reg[address_b]:
            self.fl = CPU.LESS_THAN_BIT_MASK
        else:
            self.fl = CPU.GREATER_THAN_BIT_MASK

    def bit_and(self, address_a: int, address_b: int):
        self.reg[address_a] &= self.reg[address_b]

    def bit_or(self, address_a: int, address_b: int):
        self.reg[address_a] |= self.reg[address_b]

    def bit_xor(self, address_a: int, address_b: int):
        self.reg[address_a] ^= self.reg[address_b]

    def shift_left(self, address_a: int, address_b: int):
        self.reg[address_a] <<= self.reg[address_b]

    def shift_right(self, address_a: int, address_b: int):
        self.reg[address_a] >>= self.reg[address_b]


    def jump(self):
        self.mar = self.reg[self.get_next()] - 1

    def jump_if_equal_to(self):
        if self.fl & CPU.EQUAL_TO_BIT_MASK:
            self.jump()

    def jump_if_not_equal_to(self):
        if self.fl & ~CPU.EQUAL_TO_BIT_MASK:
            self.jump()

    def jump_if_greater_than(self):
        if self.fl & CPU.GREATER_THAN_BIT_MASK:
            self.jump()

    def jump_if_less_than(self):
        if self.fl & CPU.LESS_THAN_BIT_MASK:
            self.jump()

    def jump_if_less_than_or_equal_to(self):
        if self.fl & (CPU.LESS_THAN_BIT_MASK | CPU.EQUAL_TO_BIT_MASK):
            self.jump()

    def jump_if_greater_than_or_equal_to(self):
        if self.fl & (CPU.GREATER_THAN_BIT_MASK | CPU.EQUAL_TO_BIT_MASK):
            self.jump()


    def ldi(self):
        a = self.get_next()
        b = self.get_next()
        self.reg[a] = b
        # self.reg[self.get_next()] = self.get_next() # apparently this doesn't work, not entirely sure why

    def ld(self):
        a = self.get_next()
        b = self.get_next()
        self.reg[a] = self.reg[b]
        # self.reg[self.get_next()] = self.reg[self.get_next()] # same goes for this one

    def store(self):
        pass


    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            raise Exception('use: python ls8.py <ls8 file>')

        with open(sys.argv[1]) as file_pointer:
            lines = file_pointer.readlines()
            for index, line in enumerate(lines):
                self.ram[index] = int(line.split()[0], 2)

    def ram_read(self, address: int) -> int:
        return self.ram[address]

    def ram_write(self, value: int, address: int):
        self.ram[address] = value

    def alu(self, op: str, reg_a: int, reg_b: Optional[int] = None):
        """ALU operations."""
        try:
            self.alu_ops[op](reg_a, reg_b)
        except KeyError:
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
        self.mdr = self.ram_read(self.mar)
        self.ir = self.ram_read(self.pc)
        self.commands[self.ir]()

    def run(self):
        """Run the CPU."""
        try:
            self.mar = -1
            while True:
                self.run_next_command()
        except IndexError:
            pass
        except KeyError:
            pass
        except CPU.HaltExcpetion:
            pass
        except Exception as error:
            print(error)
