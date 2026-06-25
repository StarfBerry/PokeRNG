import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from RNG import Xoroshiro128Plus

from enum import IntEnum
from typing import Iterator
from Xoroshiro_Recovery import xoroshiro_recover_seeds_with_skip

class Shiny(IntEnum):
    No = 0
    Star = 1
    Square = 2
    Yes = 3

def check_ivs(rng: Xoroshiro128Plus, ivs: list[int], fixed_ivs: int) -> bool:
    tmp_ivs = 0x3f # 0b111111
    cnt = 0

    while cnt < fixed_ivs:
        idx = rng.rand(6)
        if tmp_ivs & (1 << idx):
            if ivs[idx] != 31:
                return False
            tmp_ivs ^= 1 << idx
            cnt += 1
    
    for i in range(6):
        if (tmp_ivs & 1) and (ivs[i] != (rng.next_u64() & 31)):
            return False
        tmp_ivs >>= 1
    
    return True

def swsh_recover_raid_seeds(ec: int, pid: int, ivs: list[int]) -> Iterator[tuple[int, int]]:
    ivs31 = ivs.count(31)
    rng = Xoroshiro128Plus(0)

    for seed in xoroshiro_recover_seeds_with_skip(ec, pid):
        rng.reseed(seed)
        rng.advance(3) # ec, fake ids, pid
        s0, s1 = rng.state

        for fixed_ivs in range(1, ivs31 + 1):
            rng.restate(s0, s1)
            
            if check_ivs(rng, ivs, fixed_ivs):
                yield (seed, fixed_ivs)

def swsh_recover_random_shiny_raid_seeds(ec: int, pidl: int, ivs: list[int], shiny: Shiny) -> Iterator[tuple[int, int, int]]:
    ivs31 = ivs.count(31)
    rng = Xoroshiro128Plus(0)
    
    match shiny:
        case Shiny.Star:
            not_shiny = lambda x: x >= 16 or x == 0
        case Shiny.Square:
            not_shiny = lambda x: x != 0
        case _:
            not_shiny = lambda x: x >= 16

    for pidh in range(1 << 16):
        px = pidh ^ pidl
        for seed in xoroshiro_recover_seeds_with_skip(ec, (pidh << 16) | pidl):
            rng.reseed(seed)
            rng.advance(1) # ec
            sidtid = rng.next_u32()
            x = (sidtid >> 16) ^ (sidtid & 0xffff) ^ px

            if not_shiny(x):
                continue
            
            rng.advance(1) # pid

            s0, s1 = rng.state
            
            for fixed_ivs in range(1, ivs31 + 1):
                rng.restate(s0, s1)
                
                if check_ivs(rng, ivs, fixed_ivs):
                    yield (seed, fixed_ivs, (pidh << 16) | pidl)

def search_swsh_raid_seeds(ec: int, pid: int, ivs: list[int], shiny: Shiny = Shiny.No):   
    results = False
    
    if shiny:
        print("The search for a random shiny (not forced) is slow and will take several seconds ...")
        for seed, fixed_ivs, init_pid in swsh_recover_random_shiny_raid_seeds(ec, pid & 0xffff, ivs, shiny):
            print(f"Seed = 0x{seed:016X} | Fixed IVs = {fixed_ivs} | Initial PID = 0x{init_pid:08X}")
            results = True
    else:
        for seed, fixed_ivs in swsh_recover_raid_seeds(ec, pid, ivs):
            print(f"Seed = 0x{seed:016X} | Fixed IVs = {fixed_ivs}")
            results = True
        
        for seed, fixed_ivs in swsh_recover_raid_seeds(ec, pid ^ 0x1000_0000, ivs):
            print(f"Seed = 0x{seed:016X} | Fixed IVs = {fixed_ivs} (Shiny Lock applied)")
            results = True
    
    if not results:
        print("No results.")

if __name__ == "__main__":
    '''ec = 0x34d1c0d3
    pid = 0x3ee4c7ae
    ivs = [9, 31, 23, 18, 23, 31]
    shiny = Shiny.No'''

    ec = 0xbd5a494b
    pid = 0xd8f030c6
    ivs = [31, 31, 31, 31, 20, 31]
    shiny = Shiny.No
    
    '''ec = 0xb93c5409
    pid = 0x81286521
    ivs = [6, 11, 31, 14, 31, 31]
    shiny = Shiny.Star'''

    '''ec = 0x6ea7e950
    pid = 0x1235f63d
    ivs = [31, 31, 31, 6, 10, 23]
    shiny = Shiny.Square'''

    search_swsh_raid_seeds(ec, pid, ivs, shiny)