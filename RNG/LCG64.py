# 64-bit Linear Congruential Generator

def lcg64_jump_tables(mult: int, incr: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    mult_table = [mult]
    incr_table = [incr]
    for _ in range(63):
        incr = (incr * (mult + 1)) & 0xffffffffffffffff
        mult = (mult * mult) & 0xffffffffffffffff
        mult_table.append(mult)
        incr_table.append(incr)
    return (tuple(mult_table), tuple(incr_table))

def define_lcg64(mult: int, incr: int) -> type:
    # Hull-Dobell Theorem for maximum period (https://en.wikipedia.org/wiki/Linear_congruential_generator#m_a_power_of_2,_c_%E2%89%A0_0)
    assert mult % 4 == 1 and incr % 2 == 1, "The LCG doesn't have maximum period."

    # Maximum potency for better randomness (https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9rateur_congruentiel_lin%C3%A9aire#Le_potentiel)
    assert mult % 8 == 5, "The multiplier doesn't have maximum potency."

    mult &= 0xffffffffffffffff
    incr &= 0xffffffffffffffff

    class LCG64:
        MULT_TABLE, INCR_TABLE = lcg64_jump_tables(mult, incr)

        def __init__(self, seed: int):         
            self.state = seed & 0xffffffffffffffff

        def next_u64(self) -> int:
            self.state = (self.state * mult + incr) & 0xffffffffffffffff
            return self.state

        def next_u32(self) -> int:
            return self.next_u64() >> 32

        def rand(self, maximum: int) -> int:
            return (self.next_u32() * maximum) >> 32

        def advance(self, n: int):
            for _ in range(n):
                self.state = (self.state * mult + incr) & 0xffffffffffffffff

        def jump(self, n: int):
            while n:
                i = n.bit_length() - 1 # <==> 63 - std::countl_zero(n) in C++
                self.state = (self.state * LCG64.MULT_TABLE[i] + LCG64.INCR_TABLE[i]) & 0xffffffffffffffff
                n ^= 1 << i

        @staticmethod
        def distance(start: int, end: int) -> int:
            dist = 0
            while diff := start ^ end:
                dist |= diff & -diff # <==> diff & (~diff + 1) to isolate the lowest power of 2
                i = dist.bit_length() - 1 # <==> 63 - std::countl_zero(dist) in C++
                start = (start * LCG64.MULT_TABLE[i] + LCG64.INCR_TABLE[i]) & 0xffffffffffffffff
            return dist

    return LCG64

BWRNG = define_lcg64(0x5D588B656C078965, 0x269EC3)
BWRNGR = define_lcg64(0xDEDCEDAE9638806D, 0x9B1AE6E9A384E6F9)