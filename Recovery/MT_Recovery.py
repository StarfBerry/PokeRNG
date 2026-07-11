def mt_next_in_place(state: list[int]):
    for i in range(624):
        tmp = (state[i] & 0x80000000) | (state[(i + 1) % 624] & 0x7fffffff)            
        state[i] = state[(i + 397) % 624] ^ (tmp >> 1)
        if tmp & 1: 
            state[i] ^= 0x9908B0DF

def mt_prev_in_place(state: list[int]):
    for i in reversed(range(624)):
        tmp = state[i] ^ state[(i + 397) % 624]
        if tmp & 0x80000000:
            tmp ^= 0x9908B0DF

        state[i] = (tmp << 1) & 0x80000000

        tmp = state[(i - 1) % 624] ^ state[(i + 396) % 624]
        if tmp & 0x80000000:
            tmp ^= 0x9908B0DF
            state[i] |= 1

        state[i] |= (tmp << 1) & 0x7fffffff

def mt_initialization(seed: int) -> list[int]:
    state = [0] * 624
    
    state[0] = seed & 0xffffffff
    for i in range(1, 624):
        seed = (0x6C078965 * (seed ^ (seed >> 30)) + i) & 0xffffffff
        state[i] = seed
    
    mt_next_in_place(state)

    return state

def mt_reverse_init_step(s: int, i: int) -> int:
    s = (0x9638806D * (s - i)) & 0xffffffff
    return s ^ (s >> 30)

def mt_reverse_init_loop(s: int, p: int) -> int:
    for i in reversed(range(1, p + 1)):
        s = mt_reverse_init_step(s, i)
    return s

def mt_recover_seed_from_state(state: list[int], max_advc: int = 10_000) -> int | None:
    n = (max_advc + 623) // 624

    for _ in range(n + 1):
        s = state[1]
        if all(state[i] == (s := (0x6C078965 * (s ^ (s >> 30)) + i) & 0xffffffff) for i in range(2, 624)):
            return mt_reverse_init_step(state[1], 1)
        mt_prev_in_place(state)
    
    return None

def mt_untemper(t: int) -> int:
    t ^= t >> 18
    t ^= (t << 15) & 0xEFC60000
    t ^= (t << 7 ) & 0x9D2C5680
    t ^= (t << 14) & 0x94284000
    t ^= (t << 28) & 0x10000000
    t ^= t >> 11
    t ^= t >> 22
    return t

# Based on: https://blog.lexfo.fr/php-mt-rand-prediction.html
def mt_recover_seed_from_2_outputs(out0: int, out227: int, ofs: int = 0) -> int | None:
    """Recovers the MT seed from two outputs separated by 226 others (from the first twisted state)."""  
    assert 0 <= ofs < 396

    curr_s0 = mt_untemper(out0)
    curr_s227 = mt_untemper(out227)

    x = curr_s0 ^ curr_s227

    if prev_s228_lsb := (x >> 31):
        x ^= 0x9908B0DF

    if prev_s227_msb := ((x >> 30) & 1): 
        x ^= 0x40000000
    
    prev_s228 = (x << 1) | prev_s228_lsb
    
    if (mt_reverse_init_step(prev_s228, 228 + ofs) >> 31) != prev_s227_msb:
        prev_s228 |= 0x80000000
    
    seed = mt_reverse_init_loop(prev_s228, 228 + ofs)
    
    state = mt_initialization(seed) 

    if state[ofs] == curr_s0 and state[227 + ofs] == curr_s227:
        return seed

    return None

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from RNG import MT
    
    from random import getrandbits, randrange

    def test_mt_recover_seed_from_state(n: int = 10_000):
        mt = MT(0)

        for _ in range(n):
            seed = getrandbits(32)
            advc = randrange(0, 10_000)

            mt.reseed(seed)
            mt.advance(advc)

            seed_ = mt_recover_seed_from_state(mt.state.copy())
            assert seed == seed_, f"{seed = }, {seed_ = }, {advc = }"

    def test_mt_recover_seed_from_2_outputs(n: int = 10_000):
        mt = MT(0)

        for _ in range(n):
            seed = getrandbits(32)
            ofs = randrange(0, 396)
            
            mt.reseed(seed)
            mt.advance(ofs)
            a = mt.next_u32()
            mt.advance(226)
            b = mt.next_u32()
            
            seed_ = mt_recover_seed_from_2_outputs(a, b, ofs)
            assert seed == seed_, f"{seed = }, {seed_ = }, {ofs = }"
    

    #test_mt_recover_seed_from_state()
    
    #test_mt_recover_seed_from_2_outputs()