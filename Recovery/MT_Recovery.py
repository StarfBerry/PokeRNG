import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from RNG import MT

def mt_untemper(t: int) -> int:
    t ^= t >> 18
    t ^= (t << 15) & 0xEFC60000
    t ^= (t << 7 ) & 0x9D2C5680
    t ^= (t << 14) & 0x94284000
    t ^= (t << 28) & 0x10000000
    t ^= t >> 11
    t ^= t >> 22
    return t

def mt_reverse_init_step(s: int, i: int) -> int:
    s = (0x9638806D * (s - i)) & 0xffffffff
    return s ^ (s >> 30)

def mt_reverse_init_loop(s: int, p: int) -> int:
    for i in reversed(range(1, p + 1)):
        s = mt_reverse_init_step(s, i)
    return s

# Based on: https://blog.lexfo.fr/php-mt-rand-prediction.html
def mt_recover_seed_from_untempered_outputs(curr_s0: int, curr_s227: int, ofs: int = 0) -> int | None:
    """Recovers the MT seed with two untempered outputs separated by 226 others (from the first twisted state)."""  
    assert 0 <= ofs < 396
        
    x = curr_s0 ^ curr_s227

    if prev_s228_lsb := (x >> 31):
        x ^= 0x9908B0DF

    if prev_s227_msb := ((x >> 30) & 1): 
        x ^= 0x40000000
    
    prev_s228 = (x << 1) | prev_s228_lsb
    if (mt_reverse_init_step(prev_s228, 228 + ofs) >> 31) != prev_s227_msb:
        prev_s228 |= 0x80000000
    
    seed = mt_reverse_init_loop(prev_s228, 228 + ofs)
    
    mt = MT(seed)

    if (mt.state[ofs] == curr_s0) and (mt.state[227 + ofs] == curr_s227):
        return seed

    return None

def mt_recover_seed_from_tempered_outputs(t0: int, t227: int, ofs: int = 0): 
    u0 = mt_untemper(t0)
    u227 = mt_untemper(t227)
    return mt_recover_seed_from_untempered_outputs(u0, u227, ofs)

if __name__ == "__main__":
    from random import randrange

    mt = MT(0)
    p2 = 1 << 32
    n = 10_000

    for _ in range(n):
        seed = randrange(0, p2)
        mt.reseed(seed)

        ofs = randrange(0, 396)
        mt.advance(ofs)
        a = mt.next_u32()
        mt.advance(226)
        b = mt.next_u32()
        seed_ = mt_recover_seed_from_tempered_outputs(a, b, ofs)
        
        assert seed == seed_, f"{seed = }, {ofs = }, {seed_ = }"