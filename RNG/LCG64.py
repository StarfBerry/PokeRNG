# 64-bit Linear Congruential Generator

def jump_tables_lcg64(mult: int, inc: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    mult_table = [mult]
    inc_table = [inc]
    for _ in range(63):
        inc = (inc * (mult + 1)) & 0xffffffffffffffff
        mult = (mult * mult) & 0xffffffffffffffff
        mult_table.append(mult)
        inc_table.append(inc)
    return (tuple(mult_table), tuple(inc_table))

def define_lcg64(mult: int, inc: int) -> type:
    # Hull-Dobell Theorem for maximum period (https://en.wikipedia.org/wiki/Linear_congruential_generator#m_a_power_of_2,_c_%E2%89%A0_0)
    assert (mult % 4) == 1 and (inc % 2) == 1, "The LCG doesn't have maximum period."
    
    # Maximum potency for better randomness (https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9rateur_congruentiel_lin%C3%A9aire#Le_potentiel)
    assert (mult % 8) == 5, "The LCG doesn't have maximum potency."

    class LCG64:   
        MULT_TABLE, INC_TABLE = jump_tables_lcg64(mult, inc)

        def __init__(self, seed: int):         
            self.state = seed & 0xffffffffffffffff
        
        def next_u64(self) -> int:
            self.state = (self.state * mult + inc) & 0xffffffffffffffff
            return self.state

        def next_u32(self) -> int:
            return self.next_u64() >> 32

        def rand(self, maximum: int) -> int:
            return (self.next_u32() * maximum) >> 32

        def advance(self, n: int):
            for _ in range(n):
                self.state = (self.state * mult + inc) & 0xffffffffffffffff

        def jump(self, n: int):
            while n:
                i = n.bit_length() - 1
                self.state = (self.state * LCG64.MULT_TABLE[i] + LCG64.INC_TABLE[i]) & 0xffffffffffffffff
                n ^= 1 << i # skip zeros (at the cost of calling the bit_length method on n)
                
        @staticmethod
        def distance(s0: int, s1: int) -> int:                    
            dist = 0
            while diff := s0 ^ s1:
                dist |= diff & -diff # <==> diff & (~diff + 1) to isolate the lowest power of 2
                i = dist.bit_length() - 1 # <==> 63 - std::countl_zero(dist)
                s0 = (s0 * LCG64.MULT_TABLE[i] + LCG64.INC_TABLE[i]) & 0xffffffffffffffff
            return dist

    return LCG64

BWRNG = define_lcg64(0x5D588B656C078965, 0x269EC3)
BWRNGR = define_lcg64(0xDEDCEDAE9638806D, 0x9B1AE6E9A384E6F9)