import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from RNG import MT

from typing import Sequence

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

def mt_recover_seed_from_state(state: Sequence[int], max_advc: int = 10_000) -> int | None:
    mt = MT(state)
    n = (max_advc + 623) // 624

    for _ in range(n + 1):
        s = mt.state[1]
        if all(mt.state[i] == (s := (0x6C078965 * (s ^ (s >> 30)) + i) & 0xffffffff) for i in range(2, 624)):
            return mt_reverse_init_step(mt.state[1], 1)
        mt.untwist()
    
    return None

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

if __name__ == "__main__":
    from random import getrandbits, randrange

    def test_mt_recover_seed_from_state(n: int = 10_000):
        mt = MT(0)

        for _ in range(n):
            seed = getrandbits(32)
            advc = randrange(0, 10_000)

            mt.reseed(seed)
            mt.advance(advc)

            seed_ = mt_recover_seed_from_state(mt.state)
            assert seed == seed_, f"{seed = }, {seed_ = }, {advc = }"

    def test_mt_recover_seed_from_untempered_outputs(n: int = 10_000):
        mt = MT(0)

        for _ in range(n):
            seed = getrandbits(32)
            ofs = randrange(0, 396)
            
            mt.reseed(seed)
            mt.advance(ofs)
            a = mt.next_u32()
            mt.advance(226)
            b = mt.next_u32()
            
            seed_ = mt_recover_seed_from_untempered_outputs(mt_untemper(a), mt_untemper(b), ofs)
            assert seed == seed_, f"{seed = }, {seed_ = }, {ofs = }"
    

    #test_mt_recover_seed_from_state()
    
    #test_mt_recover_seed_from_untempered_outputs()