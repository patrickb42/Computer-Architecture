"""CPU functionality."""

import sys
from typing import Dict, List, Optional

class CPU:
    """Main CPU class."""

    LESS_THAN_BIT_MASK = 0b00000100
    GREATER_THAN_BIT_MASK = 0b00000010
    EQUAL_TO_BIT_MASK = 0b00000001

    MAX_8_BIT_VALUE = 0xFF
    BOTTOM_OF_STACK_ADDRESS = 0xF4

    def __init__(self):
        """Construct a new CPU."""
        self.instructions_size: int = 0
        self.ram: List[int] = [0] * 256
        self.reg: List[int] = [0] * 5
        self.interrupt_mask: int = 0x00 # reg 5
        self.interrupt_status: int = 0x00 # reg 6
        self.stack_pointer: int = CPU.BOTTOM_OF_STACK_ADDRESS # reg 7
        self.mem_adr_reg: int = 0 # mar
        self.mem_data_reg: int = self.ram_read(self.mem_adr_reg) # mdr
        self.program_counter_adr: int = self.mem_adr_reg # pc
        self.instruction_reg_data: int = self.ram_read(self.program_counter_adr) # ir
        self.fl: int = 0b00000000

        self.commands: Dict[int, callable] = {
            0x00: self.no_op,
            0x01: self.halt,
            0x11: self.return_from_subroutine,
            0x13: self.return_from_interrupt_handler, # finish
            0x45: self.push,
            0x46: self.pop,
            0x47: self.print_number,
            0x48: self.print_alpha,
            0x50: self.call,
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
        self.mem_adr_reg += 1
        self.mem_data_reg = self.ram_read(self.mem_adr_reg)
        return self.mem_data_reg

    def no_op(self):
        pass

    def halt(self):
        raise CPU.HaltExcpetion('halted')

    def call(self):
        self.stack_pointer -= 1
        self.ram[self.stack_pointer] = self.mem_adr_reg + 1
        if self.stack_pointer <= self.instructions_size:
            raise Exception('stack overflow')
        self.jump()

    def return_from_subroutine(self):
        if self.stack_pointer >= CPU.BOTTOM_OF_STACK_ADDRESS:
            raise Exception('cannot pop from empty stack')
        self.mem_adr_reg = self.ram[self.stack_pointer]
        self.stack_pointer += 1

    def return_from_interrupt_handler(self):
        pass

    def push(self):
        reg: int = self.get_next()
        self.stack_pointer -= 1
        if self.stack_pointer <= self.instructions_size:
            raise Exception('stack overflow')
        self.ram[self.stack_pointer] = self.reg[reg]

    def pop(self):
        if self.stack_pointer >= CPU.BOTTOM_OF_STACK_ADDRESS:
            raise Exception('cannot pop from empty stack')
        reg: int = self.get_next()
        self.reg[reg] = self.ram[self.stack_pointer]
        self.stack_pointer += 1

    def print_number(self):
        print(self.reg[self.get_next()])

    def print_alpha(self):
        print(chr(self.reg[self.get_next()]), end='')


    def increment(self, reg_address: int, _):
        self.reg[reg_address] = (self.reg[reg_address] + 1) & CPU.MAX_8_BIT_VALUE

    def decrement(self, reg_address: int, _):
        self.reg[reg_address] = (self.reg[reg_address] - 1) & CPU.MAX_8_BIT_VALUE

    def alu_not(self, reg_address: int, _):
        self.reg[reg_address] = ~self.reg[reg_address]

    def add(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] = (self.reg[reg_address_a] + self.reg[address_b])\
            & CPU.MAX_8_BIT_VALUE

    def subtract(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] = (self.reg[reg_address_a] - self.reg[address_b])\
            & CPU.MAX_8_BIT_VALUE

    def multiply(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] = (self.reg[reg_address_a] * self.reg[address_b])\
            & CPU.MAX_8_BIT_VALUE

    def divide(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] //= self.reg[address_b]

    def mod(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] %= self.reg[address_b]

    def compare(self, reg_address_a: int, address_b: int):
        if self.reg[reg_address_a] == self.reg[address_b]:
            self.fl = CPU.EQUAL_TO_BIT_MASK
        elif self.reg[reg_address_a] < self.reg[address_b]:
            self.fl = CPU.LESS_THAN_BIT_MASK
        else:
            self.fl = CPU.GREATER_THAN_BIT_MASK

    def bit_and(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] &= self.reg[address_b]

    def bit_or(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] |= self.reg[address_b]

    def bit_xor(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] ^= self.reg[address_b]

    def shift_left(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] <<= self.reg[address_b]

    def shift_right(self, reg_address_a: int, address_b: int):
        self.reg[reg_address_a] >>= self.reg[address_b]


    def jump(self, reg: int = None):
        self.mem_adr_reg = self.reg[reg if reg is not None else self.get_next()] - 1

    def jump_if_equal_to(self):
        next_reg: int = self.get_next()
        if self.fl & CPU.EQUAL_TO_BIT_MASK:
            self.jump(next_reg)

    def jump_if_not_equal_to(self):
        next_reg: int = self.get_next()
        if self.fl & ~CPU.EQUAL_TO_BIT_MASK:
            self.jump(next_reg)

    def jump_if_greater_than(self):
        next_reg: int = self.get_next()
        if self.fl & CPU.GREATER_THAN_BIT_MASK:
            self.jump(next_reg)

    def jump_if_less_than(self):
        next_reg: int = self.get_next()
        if self.fl & CPU.LESS_THAN_BIT_MASK:
            self.jump(next_reg)

    def jump_if_less_than_or_equal_to(self):
        next_reg: int = self.get_next()
        if self.fl & (CPU.LESS_THAN_BIT_MASK | CPU.EQUAL_TO_BIT_MASK):
            self.jump(next_reg)

    def jump_if_greater_than_or_equal_to(self):
        next_reg: int = self.get_next()
        if self.fl & (CPU.GREATER_THAN_BIT_MASK | CPU.EQUAL_TO_BIT_MASK):
            self.jump(next_reg)


    def ldi(self):
        a: int = self.get_next()
        b: int = self.get_next()
        self.reg[a] = b
        # self.reg[self.get_next()] = self.get_next() # apparently this doesn't work, not entirely sure why

    def ld(self):
        a: int = self.get_next()
        b: int = self.get_next()
        self.reg[a] = self.ram_read(self.reg[b])
        # self.reg[self.get_next()] = self.reg[self.get_next()] # same goes for this one

    def store(self):
        a: int = self.get_next()
        b: int = self.get_next()
        self.ram_write(self.reg[a], self.ram[self.reg[b]])


    def copy(self):
        result = CPU()
        result.reg = self.reg[:]
        result.mem_adr_reg = self.mem_adr_reg
        result.mem_data_reg = self.mem_data_reg
        result.program_counter_adr = self.program_counter_adr
        result.instruction_reg_data = self.instruction_reg_data
        result.fl = self.fl
        return result

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            raise Exception('use: python ls8.py <ls8 file>')

        with open(sys.argv[1]) as file_pointer:
            lines: List[str] = file_pointer.readlines()

            for line in lines:
                try:
                    instruction: str = line.split()[0]
                    if self.instructions_size >= CPU.BOTTOM_OF_STACK_ADDRESS:
                        raise Exception('program to large to load into RAM')
                    instruction_number_value = int(instruction, 2)
                    if instruction_number_value <= CPU.MAX_8_BIT_VALUE:
                        self.ram[self.instructions_size] = instruction_number_value
                        self.instructions_size += 1
                except Exception:
                    pass

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

        print(f"TRACE: pc: %02X | %02X %02X %02X %02X |" % (
            self.program_counter_adr,
            self.fl,
            #self.ie,
            self.ram_read(self.program_counter_adr),
            self.ram_read(self.program_counter_adr + 1),
            self.ram_read(self.program_counter_adr + 2),
        ), end='')

        for i in range(5):
            print(" %02X" % self.reg[i], end='')

        print(" im: %02X" % self.interrupt_mask, end='')
        print(" is: %02X" % self.interrupt_status, end='')
        print(" sp: %02X" % self.stack_pointer, end='')
        print(self.commands[self.ram_read(self.program_counter_adr)], end='')

        print()

    def run_next_command(self) -> bool:
        self.mem_adr_reg += 1
        self.program_counter_adr = self.mem_adr_reg
        self.mem_data_reg = self.ram_read(self.mem_adr_reg)
        self.instruction_reg_data = self.ram_read(self.program_counter_adr)
        # self.trace()
        self.commands[self.instruction_reg_data]()

    def run(self):
        """Run the CPU."""
        try:
            self.mem_adr_reg = -1
            while True:
                self.run_next_command()
        # except IndexError as error:
        #     print(error)
        # except KeyError as error:
        #     print(error)
        except CPU.HaltExcpetion:
            pass
        except Exception as error:
            print('error')
            # print(error)
