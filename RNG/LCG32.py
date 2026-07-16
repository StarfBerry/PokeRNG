# 32-bit Linear Congruential Generator

def jump_tables_lcg32(mult: int, inc: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    mult_table = [mult]
    inc_table = [inc]
    for _ in range(31):
        inc = (inc * (mult + 1)) & 0xffffffff
        mult = (mult * mult) & 0xffffffff
        mult_table.append(mult)
        inc_table.append(inc)
    return (tuple(mult_table), tuple(inc_table))

def define_lcg32(mult: int, inc: int) -> type:
    # Hull-Dobell Theorem for maximum period (https://en.wikipedia.org/wiki/Linear_congruential_generator#m_a_power_of_2,_c_%E2%89%A0_0)
    assert mult % 4 == 1 and inc % 2 == 1, "The LCG doesn't have maximum period."
    
    # Maximum potency for better randomness (https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9rateur_congruentiel_lin%C3%A9aire#Le_potentiel)
    assert mult % 8 == 5, "The multiplier doesn't have maximum potency."

    class LCG32:
        MULT_TABLE, INC_TABLE = jump_tables_lcg32(mult, inc)

        def __init__(self, seed: int):         
            self.state = seed & 0xffffffff
        
        def next_u32(self) -> int:
            self.state = (self.state * mult + inc) & 0xffffffff
            return self.state
        
        def next_u16(self) -> int:
            return self.next_u32() >> 16

        def rand_mod(self, maximum: int) -> int:
            return self.next_u16() % maximum

        def rand_div(self, maximum: int) -> int:
            return self.next_u16() // (0xffff // maximum + 1)
        
        def advance(self, n: int):
            for _ in range(n):
                self.state = (self.state * mult + inc) & 0xffffffff
                    
        def jump(self, n: int):
            while n:
                i = n.bit_length() - 1
                self.state = (self.state * LCG32.MULT_TABLE[i] + LCG32.INC_TABLE[i]) & 0xffffffff
                n ^= 1 << i # skip zeros (at the cost of calling the bit_length method on n)

        @staticmethod
        def distance(start: int, end: int) -> int:                    
            dist = 0
            while diff := start ^ end:
                dist |= diff & -diff # <==> diff & (~diff + 1) to isolate the lowest power of 2
                i = dist.bit_length() - 1 # <==> 31 - std::countl_zero(dist)
                start = (start * LCG32.MULT_TABLE[i] + LCG32.INC_TABLE[i]) & 0xffffffff
            return dist
    
    return LCG32

LCRNG = define_lcg32(0x41C64E6D, 0x6073)
LCRNGR = define_lcg32(0xEEB9EB65, 0xA3561A1)

MRNG = define_lcg32(0x41C64E6D, 0x3039)
MRNGR = define_lcg32(0xEEB9EB65, 0xFC77A683) 

GCRNG = define_lcg32(0x343FD, 0x269EC3)
GCRNGR = define_lcg32(0xB9B33155, 0xA170F641)

ARNG = define_lcg32(0x6C078965, 0x1)
ARNGR = define_lcg32(0x9638806D, 0x69C77F93)